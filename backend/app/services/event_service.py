from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import datetime

from app.db import (
    Event,
    EventParticipant,
    EventGallery,
    Volunteer,
    Organization,
    ParticipationStatus,
)
from app.schemas import EventCreate


class EventService:
    def __init__(self, db: Session):
        self.db = db

    def create_event(self, event_data: EventCreate) -> Event:
        """Create a new event."""
        # Check if organization exists
        org = (
            self.db.query(Organization)
            .filter(Organization.id == event_data.organization_id)
            .first()
        )
        if not org:
            raise ValueError("Organization not found")

        # Create the event
        db_event = Event(
            title=event_data.title,
            event_type=event_data.event_type,
            organization_id=event_data.organization_id,
            location=event_data.location,
            latitude=event_data.latitude,
            longitude=event_data.longitude,
            start_time=event_data.start_time,
            end_time=event_data.end_time,
            is_emergency=event_data.is_emergency,
            emergency_contact=event_data.emergency_contact,
        )

        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return db_event

    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Get event by ID with related data."""
        return (
            self.db.query(Event)
            .options(
                joinedload(Event.organization),
                joinedload(Event.participants),
                joinedload(Event.resources),
            )
            .filter(Event.id == event_id)
            .first()
        )

    def get_events(
        self,
        skip: int = 0,
        limit: int = 20,
        upcoming_only: bool = False,
        event_type: Optional[str] = None,
        is_emergency: Optional[bool] = None,
    ) -> List[Event]:
        """Get events with filtering options."""
        query = self.db.query(Event)

        # Apply filters
        if upcoming_only:
            query = query.filter(Event.start_time >= datetime.utcnow())

        if event_type:
            query = query.filter(Event.event_type == event_type)

        if is_emergency is not None:
            query = query.filter(Event.is_emergency == is_emergency)

        # Order by start time
        query = query.order_by(Event.start_time)

        return query.offset(skip).limit(limit).all()

    def get_nearby_events(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0,
        upcoming_only: bool = True,
    ) -> List[Tuple[Event, float]]:
        """
        Get events near a location within a radius.
        Returns list of tuples (event, distance_km)
        """
        # Using Haversine formula to calculate distances
        # Note: A more sophisticated implementation would use PostGIS or similar
        earth_radius_km = 6371.0

        # Calculate distance using SQL
        distance = (
            func.acos(
                func.sin(func.radians(latitude))
                * func.sin(func.radians(Event.latitude))
                + func.cos(func.radians(latitude))
                * func.cos(func.radians(Event.latitude))
                * func.cos(func.radians(Event.longitude) - func.radians(longitude))
            )
            * earth_radius_km
        )

        query = self.db.query(Event, distance.label("distance"))

        # Filter by distance and upcoming if requested
        query = query.filter(distance <= radius_km)
        if upcoming_only:
            query = query.filter(Event.start_time >= datetime.utcnow())

        # Order by distance
        query = query.order_by("distance")

        return [(event, dist) for event, dist in query.all()]

    def register_participant(
        self, event_id: int, volunteer_id: int
    ) -> EventParticipant:
        """Register a volunteer for an event."""
        # Check if already registered
        existing = (
            self.db.query(EventParticipant)
            .filter(
                EventParticipant.event_id == event_id,
                EventParticipant.volunteer_id == volunteer_id,
            )
            .first()
        )

        if existing:
            return existing

        # Register new participant
        participant = EventParticipant(
            event_id=event_id,
            volunteer_id=volunteer_id,
            status=ParticipationStatus.REGISTERED,
        )

        self.db.add(participant)
        self.db.commit()
        self.db.refresh(participant)
        return participant

    def update_participant_status(
        self, event_id: int, volunteer_id: int, status: ParticipationStatus
    ) -> Optional[EventParticipant]:
        """Update the status of a participant."""
        participant = (
            self.db.query(EventParticipant)
            .filter(
                EventParticipant.event_id == event_id,
                EventParticipant.volunteer_id == volunteer_id,
            )
            .first()
        )

        if not participant:
            return None

        participant.status = status
        self.db.commit()
        self.db.refresh(participant)
        return participant

    def add_event_image(
        self, event_id: int, image_url: str, caption: Optional[str] = None
    ) -> EventGallery:
        """Add an image to the event gallery."""
        gallery_item = EventGallery(
            event_id=event_id, image_url=image_url, caption=caption
        )

        self.db.add(gallery_item)
        self.db.commit()
        self.db.refresh(gallery_item)
        return gallery_item
