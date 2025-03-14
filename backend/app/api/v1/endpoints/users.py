from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.v1.dependencies import get_current_user
from app.db import get_db, User
from app.schemas import UserUpdate, UserResponse, UserRoleCreate, UserRoleEnum
from app.services import user_service

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Get current user information.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user(
    *,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user information.
    """
    return user_service.update_user(db, current_user.id, user_data)


@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get user by ID.
    """
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
    # Check if user is admin
    if not current_user.has_role(UserRoleEnum.ADMIN.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    users = user_service.get_users(db, skip=skip, limit=limit)
    return users


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
    # Check if user is admin
    if not current_user.has_role(UserRoleEnum.ADMIN.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

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
    # Check if user is admin
    if not current_user.has_role(UserRoleEnum.ADMIN.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    success = user_service.remove_role_from_user(db, user_id, role)
    if not success:
        raise HTTPException(status_code=404, detail="Role not found")

    return {"message": "Role removed successfully"}
