from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.v1.dependencies import get_current_user
from app.db import get_db, User
from app.schemas import UserUpdate, UserResponse, UserRoleCreate, UserRoleEnum
from app.services import user_service, auth_service

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Get current user information.
    """
    return current_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    *,
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a user by ID.
    """
    # Check if user is super admin or organization admin with rights to manage this user
    if not (
        auth_service.is_super_admin(current_user)
        or auth_service.can_manage_user(current_user, user_id, db)
        or current_user.id == user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this user",
        )

    updated_user = user_service.update_user(db, user_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return updated_user


@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get user by ID.
    """
    # Users can always see their own profile
    if current_user.id == user_id:
        return current_user

    # Super admin can see any user
    if auth_service.is_super_admin(current_user):
        user = user_service.get_user(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    # Organization admins can only see users in their organization
    if current_user.has_role(UserRoleEnum.ADMIN.value):
        if not auth_service.can_manage_user(current_user, user_id, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view users in your organization",
            )

        user = user_service.get_user(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    # For now, we'll allow regular users to see other user profiles
    # This depends on your application's requirements and can be restricted further
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List users with pagination.
    """
    # Super admin can see all users
    if auth_service.is_super_admin(current_user):
        users = user_service.get_users(db, skip=skip, limit=limit)
        return users

    # Organization admins can only see users in their organizations
    if current_user.has_role(UserRoleEnum.ADMIN.value):
        # Get organizations where current user is admin
        admin_orgs = user_service.get_user_organizations(db, current_user.id)
        admin_org_ids = [
            org.id
            for org in admin_orgs
            if any(
                m.role == UserRoleEnum.ADMIN.value and m.user_id == current_user.id
                for m in org.members
            )
        ]

        # Get users from these organizations
        if admin_org_ids:
            users = user_service.get_organization_users(
                db, admin_org_ids, skip=skip, limit=limit
            )
            return users

        # Admin without organizations can only see themselves
        return [current_user]

    # Regular users can't list users
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions",
    )


@router.post("/{user_id}/roles", response_model=UserResponse)
def add_role_to_user(
    *,
    user_id: int,
    role_data: UserRoleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a role to a user.
    """
    # Get the target user
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Super admin can add any role
    if auth_service.is_super_admin(current_user):
        user_service.add_role_to_user(db, user_id, role_data.role)
        return user_service.get_user(db, user_id)

    # Organization admins can only modify users in their organization
    if current_user.has_role(UserRoleEnum.ADMIN.value):
        # Check if admin can manage this user
        if not auth_service.can_manage_user(current_user, user_id, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only manage users in your organization",
            )

        # Prevent organization admins from adding admin or super_admin roles
        if role_data.role in [UserRoleEnum.ADMIN, UserRoleEnum.SUPER_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot assign Admin or Super Admin roles",
            )

        user_service.add_role_to_user(db, user_id, role_data.role)
        return user_service.get_user(db, user_id)

    # Regular users can only modify themselves
    # Prevent regular users from adding admin or super_admin roles
    if role_data.role in [UserRoleEnum.ADMIN, UserRoleEnum.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot assign Admin or Super Admin roles",
        )

    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify yourself",
        )

    user_service.add_role_to_user(db, user_id, role_data.role)
    return user_service.get_user(db, user_id)


@router.delete("/{user_id}/roles/{role}")
def remove_role_from_user(
    *,
    user_id: int,
    role: UserRoleEnum,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a role from a user.
    """
    # Super admin can remove any role except SUPER_ADMIN from others
    if auth_service.is_super_admin(current_user):
        # Prevent removing the last super admin role
        if role == UserRoleEnum.SUPER_ADMIN:
            # Count super admins
            super_admin_count = user_service.count_users_with_role(
                db, UserRoleEnum.SUPER_ADMIN
            )
            if super_admin_count <= 1 and user_id == current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot remove the last super admin role",
                )

        success = user_service.remove_role_from_user(db, user_id, role)
        if not success:
            raise HTTPException(status_code=404, detail="Role not found")

        return {"message": "Role removed successfully"}

    # Organization admins can only modify users in their organization
    if current_user.has_role(UserRoleEnum.ADMIN.value):
        # Check if admin can manage this user
        if not auth_service.can_manage_user(current_user, user_id, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only manage users in your organization",
            )

        # Prevent organization admins from removing admin or super_admin roles
        if role in [UserRoleEnum.ADMIN, UserRoleEnum.SUPER_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot remove Admin or Super Admin roles",
            )

        success = user_service.remove_role_from_user(db, user_id, role)
        if not success:
            raise HTTPException(status_code=404, detail="Role not found")

        return {"message": "Role removed successfully"}

    # Regular users can only modify themselves
    # Prevent regular users from removing admin or super_admin roles
    if role in [UserRoleEnum.ADMIN, UserRoleEnum.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot remove Admin or Super Admin roles",
        )

    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify yourself",
        )

    success = user_service.remove_role_from_user(db, user_id, role)
    if not success:
        raise HTTPException(status_code=404, detail="Role not found")
