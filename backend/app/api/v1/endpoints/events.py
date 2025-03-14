from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.v1.dependencies import get_current_user
from app.db import get_db, User
from app.schemas import (
    EventCreate,
    EventUpdate,
    EventResponse,
    EventCollaboratorCreate,
    EventBeneficiaryCreate,
    UserResponse,
    UserRoleEnum,
)
from app.services import event_service, organization_service

router = APIRouter()


@router.post("/", response_model=EventResponse)
def create_event(
    *,
    event_data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new event.
    """
    # Check if user is a member with admin role in the organization
    orgs = organization_service.get_user_organizations(db, current_user.id)
    is_admin = any(
        org.id == event_data.organization_id
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
            detail="Not enough permissions to create an event for this organization",
        )

    try:
        return event_service.create_event(db, event_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=List[EventResponse])
def list_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List all events with pagination.
    """
    return event_service.get_events(db, skip=skip, limit=limit)


@router.get("/upcoming", response_model=List[EventResponse])
def upcoming_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get upcoming events.
    """
    return event_service.get_upcoming_events(db, skip=skip, limit=limit)


@router.get("/organization/{organization_id}", response_model=List[EventResponse])
def organization_events(organization_id: int, db: Session = Depends(get_db)):
    """
    Get events for a specific organization.
    """
    org = organization_service.get_organization(db, organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    return event_service.get_events_by_organization(db, organization_id)


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """
    Get event by ID.
    """
    event = event_service.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    *,
    event_id: int,
    event_data: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an event.
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

    updated_event = event_service.update_event(db, event_id, event_data)
    return updated_event


@router.delete("/{event_id}")
def delete_event(
    *,
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an event.
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

    success = event_service.delete_event(db, event_id)
    return {"message": "Event deleted successfully"}


@router.post("/{event_id}/collaborators")
def add_collaborator(
    *,
    event_id: int,
    collaborator_data: EventCollaboratorCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a collaborating organization to an event.
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

    collaborator = event_service.add_collaborator_to_event(
        db, event_id, collaborator_data
    )
    if not collaborator:
        raise HTTPException(status_code=404, detail="Organization not found")

    return {"message": "Collaborator added successfully"}


@router.delete("/{event_id}/collaborators/{organization_id}")
def remove_collaborator(
    *,
    event_id: int,
    organization_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a collaborating organization from an event.
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

    success = event_service.remove_collaborator_from_event(
        db, event_id, organization_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Collaborator not found")

    return {"message": "Collaborator removed successfully"}


@router.post("/{event_id}/beneficiaries")
def add_beneficiary(
    *,
    event_id: int,
    beneficiary_data: EventBeneficiaryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a beneficiary to an event.
    """
    event = event_service.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if user is a worker in the organization
    orgs = organization_service.get_user_organizations(db, current_user.id)
    is_worker = any(
        org.id == event.organization_id
        and any(
            m.role in [UserRoleEnum.ADMIN.value, UserRoleEnum.WORKER.value]
            for m in org.members
            if m.user_id == current_user.id
        )
        for org in orgs
    )

    if not is_worker:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    beneficiary = event_service.add_beneficiary_to_event(db, event_id, beneficiary_data)
    if not beneficiary:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "Beneficiary added successfully"}


@router.get("/{event_id}/beneficiaries", response_model=List[UserResponse])
def list_beneficiaries(event_id: int, db: Session = Depends(get_db)):
    """
    List all beneficiaries for an event.
    """
    event = event_service.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return event_service.get_event_beneficiaries(db, event_id)
