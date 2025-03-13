from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.db import (
    ResourceRequest,
    ResourceContribution,
    Event,
    Volunteer,
    Organizer,
)
from app.schemas import ResourceRequestCreate


class ResourceService:
    def __init__(self, db: Session):
        self.db = db

    def create_resource_request(
        self, request_data: ResourceRequestCreate, event_id: int
    ) -> ResourceRequest:
        """Create a new resource request for an event."""
        # Verify event exists
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise ValueError("Event not found")

        # Create resource request
        resource_req = ResourceRequest(
            event_id=event_id,
            resource_type=request_data.resource_type,
            quantity_needed=request_data.quantity_needed,
            urgency_level=request_data.urgency_level,
            quantity_received=0,  # Initially no contributions
        )

        self.db.add(resource_req)
        self.db.commit()
        self.db.refresh(resource_req)
        return resource_req

    def get_resource_request(self, request_id: int) -> Optional[ResourceRequest]:
        """Get a resource request by ID with contributions."""
        return (
            self.db.query(ResourceRequest)
            .options(joinedload(ResourceRequest.contributions))
            .filter(ResourceRequest.id == request_id)
            .first()
        )

    def get_resource_requests_by_event(self, event_id: int) -> List[ResourceRequest]:
        """Get all resource requests for an event."""
        return (
            self.db.query(ResourceRequest)
            .filter(ResourceRequest.event_id == event_id)
            .all()
        )

    def create_contribution(
        self, request_id: int, volunteer_id: int, quantity: int
    ) -> ResourceContribution:
        """Record a volunteer's contribution to a resource request."""
        # Verify request exists
        resource_req = (
            self.db.query(ResourceRequest)
            .filter(ResourceRequest.id == request_id)
            .first()
        )
        if not resource_req:
            raise ValueError("Resource request not found")

        # Verify volunteer exists
        volunteer = (
            self.db.query(Volunteer).filter(Volunteer.id == volunteer_id).first()
        )
        if not volunteer:
            raise ValueError("Volunteer not found")

        # Create contribution
        contribution = ResourceContribution(
            request_id=request_id,
            volunteer_id=volunteer_id,
            quantity=quantity,
            delivery_confirmed=False,
        )

        self.db.add(contribution)

        # Update the received quantity on the request
        resource_req.quantity_received += quantity

        self.db.commit()
        self.db.refresh(contribution)
        return contribution

    def confirm_contribution(
        self, contribution_id: int, organizer_id: int
    ) -> Optional[ResourceContribution]:
        """Confirm a resource contribution was received."""
        # Verify organizer exists
        organizer = (
            self.db.query(Organizer).filter(Organizer.id == organizer_id).first()
        )
        if not organizer:
            raise ValueError("Organizer not found")

        # Get contribution
        contribution = (
            self.db.query(ResourceContribution)
            .filter(ResourceContribution.id == contribution_id)
            .first()
        )

        if not contribution:
            return None

        # Update confirmation
        contribution.delivery_confirmed = True
        contribution.confirmed_by = organizer_id

        self.db.commit()
        self.db.refresh(contribution)
        return contribution
