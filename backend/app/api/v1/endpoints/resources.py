from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.v1.dependencies import get_current_user
from app.db import get_db, User
from app.schemas import (
    ResourceRequestCreate,
    ResourceRequestUpdate,
    ResourceRequestResponse,
    ResourceContributionCreate,
    ResourceContributionResponse,
    UserRoleEnum,
)
from app.services import resource_service, organization_service, event_service

router = APIRouter()


@router.post("/requests/event/{event_id}", response_model=ResourceRequestResponse)
def create_resource_request(
    *,
    event_id: int,
    request_data: ResourceRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new resource request for an event.
    """
    event = event_service.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if user is a member with admin role in the organization
    orgs = organization_service.get_user_organizations(db, current_user.id)
    is_admin = any(
        org.id == event.organization_id
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

    request = resource_service.create_resource_request(db, event_id, request_data)
    if not request:
        raise HTTPException(status_code=404, detail="Failed to create resource request")

    return request


@router.get("/requests/event/{event_id}", response_model=List[ResourceRequestResponse])
def list_event_resource_requests(event_id: int, db: Session = Depends(get_db)):
    """
    List all resource requests for an event.
    """
    event = event_service.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return resource_service.get_resource_requests_by_event(db, event_id)


@router.put("/requests/{request_id}", response_model=ResourceRequestResponse)
def update_resource_request(
    *,
    request_id: int,
    request_data: ResourceRequestUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a resource request.
    """
    req = resource_service.get_resource_request(db, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Resource request not found")

    event = event_service.get_event(db, req.event_id)

    # Check if user is a member with admin role in the organization
    orgs = organization_service.get_user_organizations(db, current_user.id)
    is_admin = any(
        org.id == event.organization_id
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

    updated_request = resource_service.update_resource_request(
        db, request_id, request_data
    )
    return updated_request


@router.delete("/requests/{request_id}")
def delete_resource_request(
    *,
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a resource request.
    """
    req = resource_service.get_resource_request(db, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Resource request not found")

    event = event_service.get_event(db, req.event_id)

    # Check if user is a member with admin role in the organization
    orgs = organization_service.get_user_organizations(db, current_user.id)
    is_admin = any(
        org.id == event.organization_id
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

    success = resource_service.delete_resource_request(db, request_id)
    if not success:
        raise HTTPException(status_code=404, detail="Failed to delete resource request")

    return {"message": "Resource request deleted successfully"}


@router.post("/contributions", response_model=ResourceContributionResponse)
def create_contribution(
    *,
    contribution_data: ResourceContributionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new resource contribution.
    """
    contribution = resource_service.create_resource_contribution(
        db, current_user.id, contribution_data
    )
    if not contribution:
        raise HTTPException(status_code=404, detail="Failed to create contribution")

    return contribution


@router.get("/contributions/user", response_model=List[ResourceContributionResponse])
def get_user_contributions(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get all contributions made by the current user.
    """
    return resource_service.get_contributions_by_user(db, current_user.id)


@router.get(
    "/contributions/request/{request_id}",
    response_model=List[ResourceContributionResponse],
)
def get_request_contributions(request_id: int, db: Session = Depends(get_db)):
    """
    Get all contributions for a specific resource request.
    """
    req = resource_service.get_resource_request(db, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Resource request not found")

    return resource_service.get_contributions_by_request(db, request_id)
