from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models import Event, EventCollaborator, Organization, EventBeneficiary, User
from app.schemas import (
    EventCreate,
    EventUpdate,
    EventCollaboratorCreate,
    EventBeneficiaryCreate,
)
from datetime import datetime


def get_event(db: Session, event_id: int) -> Optional[Event]:
    """Get an event by ID."""
    return db.query(Event).filter(Event.id == event_id).first()


def get_events(db: Session, skip: int = 0, limit: int = 100) -> List[Event]:
    """Get all events with pagination."""
    return db.query(Event).offset(skip).limit(limit).all()


def get_events_by_organization(db: Session, organization_id: int) -> List[Event]:
    """Get events for a specific organization."""
    return db.query(Event).filter(Event.organization_id == organization_id).all()


def get_upcoming_events(db: Session, skip: int = 0, limit: int = 100) -> List[Event]:
    """Get upcoming events."""
    now = datetime.now(datetime.timezone.utc)
    return (
        db.query(Event)
        .filter(Event.start_time > now)
        .order_by(Event.start_time)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_event(db: Session, event_data: EventCreate) -> Event:
    """Create a new event."""
    # Check if organization exists
    org = (
        db.query(Organization)
        .filter(Organization.id == event_data.organization_id)
        .first()
    )
    if not org:
        raise ValueError("Organization does not exist")

    # Create event
    db_event = Event(
        title=event_data.title,
        event_type=event_data.event_type,
        start_time=event_data.start_time,
        end_time=event_data.end_time,
        organization_id=event_data.organization_id,
    )

    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    return db_event


def update_event(
    db: Session, event_id: int, event_data: EventUpdate
) -> Optional[Event]:
    """Update an event."""
    db_event = get_event(db, event_id)
    if not db_event:
        return None

    # Update fields if provided
    update_data = event_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_event, field, value)

    db.commit()
    db.refresh(db_event)
    return db_event


def delete_event(db: Session, event_id: int) -> bool:
    """Delete an event."""
    db_event = get_event(db, event_id)
    if not db_event:
        return False

    db.delete(db_event)
    db.commit()
    return True


def add_collaborator_to_event(
    db: Session, event_id: int, collaborator_data: EventCollaboratorCreate
) -> Optional[EventCollaborator]:
    """Add a collaborating organization to an event."""
    # Check if event exists
    db_event = get_event(db, event_id)
    if not db_event:
        return None

    # Check if organization exists
    org = (
        db.query(Organization)
        .filter(Organization.id == collaborator_data.organization_id)
        .first()
    )
    if not org:
        return None

    # Check if already a collaborator
    existing_collaborator = (
        db.query(EventCollaborator)
        .filter(
            EventCollaborator.event_id == event_id,
            EventCollaborator.organization_id == collaborator_data.organization_id,
        )
        .first()
    )

    if existing_collaborator:
        return existing_collaborator

    # Add new collaborator
    collaborator = EventCollaborator(
        event_id=event_id,
        organization_id=collaborator_data.organization_id,
    )

    db.add(collaborator)
    db.commit()
    db.refresh(collaborator)
    return collaborator


def remove_collaborator_from_event(
    db: Session, event_id: int, organization_id: int
) -> bool:
    """Remove a collaborating organization from an event."""
    collaborator = (
        db.query(EventCollaborator)
        .filter(
            EventCollaborator.event_id == event_id,
            EventCollaborator.organization_id == organization_id,
        )
        .first()
    )

    if not collaborator:
        return False

    db.delete(collaborator)
    db.commit()
    return True


def get_event_collaborators(db: Session, event_id: int) -> List[Organization]:
    """Get all collaborating organizations for an event."""
    collaborators = (
        db.query(EventCollaborator).filter(EventCollaborator.event_id == event_id).all()
    )

    org_ids = [c.organization_id for c in collaborators]
    return db.query(Organization).filter(Organization.id.in_(org_ids)).all()


def add_beneficiary_to_event(
    db: Session, event_id: int, beneficiary_data: EventBeneficiaryCreate
) -> Optional[EventBeneficiary]:
    """Add a beneficiary to an event."""
    # Check if event exists
    db_event = get_event(db, event_id)
    if not db_event:
        return None

    # Check if user exists
    user = db.query(User).filter(User.id == beneficiary_data.user_id).first()
    if not user:
        return None

    # Check if already a beneficiary
    existing_beneficiary = (
        db.query(EventBeneficiary)
        .filter(
            EventBeneficiary.event_id == event_id,
            EventBeneficiary.user_id == beneficiary_data.user_id,
        )
        .first()
    )

    if existing_beneficiary:
        return existing_beneficiary

    # Add new beneficiary
    beneficiary = EventBeneficiary(
        event_id=event_id,
        user_id=beneficiary_data.user_id,
        benefit_time=datetime.now(datetime.timezone.utc),
    )

    db.add(beneficiary)
    db.commit()
    db.refresh(beneficiary)
    return beneficiary


def get_event_beneficiaries(db: Session, event_id: int) -> List[User]:
    """Get all beneficiaries for an event."""
    beneficiaries = (
        db.query(EventBeneficiary).filter(EventBeneficiary.event_id == event_id).all()
    )

    user_ids = [b.user_id for b in beneficiaries]
    return db.query(User).filter(User.id.in_(user_ids)).all()
