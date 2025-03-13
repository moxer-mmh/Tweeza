# backend/app/schemas/event.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .organization import OrganizationResponse
from .volunteer import VolunteerResponse
from .resource import ResourceResponse


class EventBase(BaseModel):
    title: str
    event_type: str
    location: str
    latitude: float
    longitude: float
    start_time: datetime
    end_time: datetime
    is_emergency: bool = False
    emergency_contact: Optional[str] = None


class EventCreate(EventBase):
    organization_id: int


class EventResponse(EventBase):
    id: int
    organization: OrganizationResponse
    participants: list["VolunteerResponse"] = []
    resources: list["ResourceResponse"] = []

    class Config:
        orm_mode = True
