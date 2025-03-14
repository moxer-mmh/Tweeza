from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.v1.dependencies import get_current_user
from app.db import get_db, User
from app.schemas import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationMemberCreate,
    OrganizationMemberResponse,
    UserRoleEnum,
)
from app.services import organization_service

router = APIRouter()


@router.post("/", response_model=OrganizationResponse)
def create_organization(
    *,
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new organization.
    """
    try:
        return organization_service.create_organization(db, org_data, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=List[OrganizationResponse])
def list_organizations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List all organizations with pagination.
    """
    return organization_service.get_organizations(db, skip=skip, limit=limit)


@router.get("/my-organizations", response_model=List[OrganizationResponse])
def my_organizations(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get organizations where the current user is a member.
    """
    return organization_service.get_user_organizations(db, current_user.id)


@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(organization_id: int, db: Session = Depends(get_db)):
    """
    Get organization by ID.
    """
    org = organization_service.get_organization(db, organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.put("/{organization_id}", response_model=OrganizationResponse)
def update_organization(
    *,
    organization_id: int,
    org_data: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an organization.
    """
    # Check if user is a member with admin role
    orgs = organization_service.get_user_organizations(db, current_user.id)
    is_admin = any(
        org.id == organization_id
        and any(
            m.role == UserRoleEnum.ADMIN.value
            for m in org.members
            if m.user_id == current_user.id
        )
        for org in orgs
    )

    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    try:
        updated_org = organization_service.update_organization(
            db, organization_id, org_data
        )
        if not updated_org:
            raise HTTPException(status_code=404, detail="Organization not found")
        return updated_org
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{organization_id}")
def delete_organization(
    *,
    organization_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an organization.
    """
    # Check if user is a member with admin role
    orgs = organization_service.get_user_organizations(db, current_user.id)
    is_admin = any(
        org.id == organization_id
        and any(
            m.role == UserRoleEnum.ADMIN.value
            for m in org.members
            if m.user_id == current_user.id
        )
        for org in orgs
    )

    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    success = organization_service.delete_organization(db, organization_id)
    if not success:
        raise HTTPException(status_code=404, detail="Organization not found")

    return {"message": "Organization deleted successfully"}


@router.post("/{organization_id}/members", response_model=OrganizationMemberResponse)
def add_member(
    *,
    organization_id: int,
    member_data: OrganizationMemberCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a member to organization.
    """
    # Check if user is a member with admin role
    orgs = organization_service.get_user_organizations(db, current_user.id)
    is_admin = any(
        org.id == organization_id
        and any(
            m.role == UserRoleEnum.ADMIN.value
            for m in org.members
            if m.user_id == current_user.id
        )
        for org in orgs
    )

    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    member = organization_service.add_member_to_organization(
        db, organization_id, member_data
    )
    if not member:
        raise HTTPException(status_code=404, detail="User or organization not found")

    return member


@router.delete("/{organization_id}/members/{user_id}")
def remove_member(
    *,
    organization_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a member from organization.
    """
    # Check if user is a member with admin role
    orgs = organization_service.get_user_organizations(db, current_user.id)
    is_admin = any(
        org.id == organization_id
        and any(
            m.role == UserRoleEnum.ADMIN.value
            for m in org.members
            if m.user_id == current_user.id
        )
        for org in orgs
    )

    if not is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    success = organization_service.remove_member_from_organization(
        db, organization_id, user_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Member not found")

    return {"message": "Member removed successfully"}


@router.get(
    "/{organization_id}/members", response_model=List[OrganizationMemberResponse]
)
def list_members(organization_id: int, db: Session = Depends(get_db)):
    """
    List all members of an organization.
    """
    members = organization_service.get_organization_members(db, organization_id)
    if not members and not organization_service.get_organization(db, organization_id):
        raise HTTPException(status_code=404, detail="Organization not found")

    return members
