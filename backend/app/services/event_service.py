from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models import Event, EventCollaborator, Organization, EventBeneficiary, User
from app.schemas import (
    EventCreate,
    EventUpdate,
    EventCollaboratorCreate,
    EventBeneficiaryCreate,
)
from datetime import datetime, timezone
import math
from sqlalchemy import func


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
    now = datetime.now(timezone.utc)
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
        # Add geolocation data
        latitude=event_data.latitude,
        longitude=event_data.longitude,
        address=event_data.address,
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
        benefit_time=datetime.now(timezone.utc),
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


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points
    on the earth using the Haversine formula.
    Returns distance in kilometers.
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r


def get_nearby_events(
    db: Session,
    latitude: float,
    longitude: float,
    radius: float = 5.0,  # Default 5km radius
    event_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Event]:
    """
    Find events within a certain radius (in kilometers) from a given location.
    Optionally filter by event type.
    """
    # Approximate conversion from distance in kilometers to degrees
    # 1 degree of latitude is approximately 111 kilometers
    degree_radius = radius / 111.0

    # Base query for events
    query = db.query(Event)

    # Filter by coordinates - this is a simple approximation using a square boundary
    query = query.filter(
        Event.latitude.between(latitude - degree_radius, latitude + degree_radius),
        Event.longitude.between(longitude - degree_radius, longitude + degree_radius),
    )

    # Filter by event type if provided
    if event_type:
        query = query.filter(Event.event_type == event_type)

    # Get candidate events that are roughly within the square boundary
    candidates = query.all()

    # Further filter using actual haversine distance calculation
    nearby_events = []
    for event in candidates:
        # Skip events without coordinates
        if event.latitude is None or event.longitude is None:
            continue

        # Calculate distance using Haversine formula
        distance = calculate_distance(
            latitude, longitude, event.latitude, event.longitude
        )

        # Include event if within the specified radius
        if distance <= radius:
            # Add distance as attribute to event
            event.distance = distance
            nearby_events.append(event)

    # Sort by distance
    nearby_events.sort(key=lambda x: x.distance)

    # Apply skip and limit
    return nearby_events[skip : skip + limit]


def search_events_by_address(
    db: Session,
    address_query: str,
    event_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Event]:
    """
    Search for events by address text.
    Optionally filter by event type.
    """
    # Base query
    query = db.query(Event)

    # Search in address field using LIKE
    query = query.filter(Event.address.ilike(f"%{address_query}%"))

    # Filter by event type if provided
    if event_type:
        query = query.filter(Event.event_type == event_type)

    # Apply ordering, skip and limit
    return query.order_by(Event.start_time).offset(skip).limit(limit).all()
