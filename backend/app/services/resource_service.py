from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models import ResourceRequest, ResourceContribution, User, Event
from app.schemas import (
    ResourceRequestCreate,
    ResourceRequestUpdate,
    ResourceContributionCreate,
)
from datetime import datetime


def get_resource_request(db: Session, request_id: int) -> Optional[ResourceRequest]:
    """Get a resource request by ID."""
    return db.query(ResourceRequest).filter(ResourceRequest.id == request_id).first()


def get_resource_requests_by_event(db: Session, event_id: int) -> List[ResourceRequest]:
    """Get resource requests for a specific event."""
    return db.query(ResourceRequest).filter(ResourceRequest.event_id == event_id).all()


def create_resource_request(
    db: Session, event_id: int, request_data: ResourceRequestCreate
) -> Optional[ResourceRequest]:
    """Create a new resource request for an event."""
    # Check if event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return None

    # Create resource request
    db_request = ResourceRequest(
        event_id=event_id,
        resource_type=request_data.resource_type,
        quantity_needed=request_data.quantity_needed,
        quantity_received=0,
    )

    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    return db_request


def update_resource_request(
    db: Session, request_id: int, request_data: ResourceRequestUpdate
) -> Optional[ResourceRequest]:
    """Update a resource request."""
    db_request = get_resource_request(db, request_id)
    if not db_request:
        return None

    # Update fields if provided
    update_data = request_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_request, field, value)

    db.commit()
    db.refresh(db_request)
    return db_request


def delete_resource_request(db: Session, request_id: int) -> bool:
    """Delete a resource request."""
    db_request = get_resource_request(db, request_id)
    if not db_request:
        return False

    db.delete(db_request)
    db.commit()
    return True


def create_resource_contribution(
    db: Session, user_id: int, contribution_data: ResourceContributionCreate
) -> Optional[ResourceContribution]:
    """Create a new resource contribution."""
    # Check if request exists
    request = get_resource_request(db, contribution_data.request_id)
    if not request:
        return None

    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    # Create contribution
    db_contribution = ResourceContribution(
        request_id=contribution_data.request_id,
        user_id=user_id,
        quantity=contribution_data.quantity,
        contribution_time=datetime.utcnow(),
    )

    db.add(db_contribution)

    # Update quantity received in the request
    request.quantity_received += contribution_data.quantity

    db.commit()
    db.refresh(db_contribution)

    return db_contribution


def get_contributions_by_user(db: Session, user_id: int) -> List[ResourceContribution]:
    """Get all contributions made by a user."""
    return (
        db.query(ResourceContribution)
        .filter(ResourceContribution.user_id == user_id)
        .all()
    )


def get_contributions_by_request(
    db: Session, request_id: int
) -> List[ResourceContribution]:
    """Get all contributions for a specific request."""
    return (
        db.query(ResourceContribution)
        .filter(ResourceContribution.request_id == request_id)
        .all()
    )
