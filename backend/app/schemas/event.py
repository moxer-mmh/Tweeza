from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class EventTypeEnum(str, Enum):
    IFTAR = "iftar"
    CLEANUP = "cleanup"
    EMERGENCY = "emergency"
    WORKSHOP = "workshop"


class EventBase(BaseModel):
    title: str
    event_type: EventTypeEnum
    start_time: datetime
    end_time: datetime
    organization_id: int


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = None
    event_type: Optional[EventTypeEnum] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class EventResponse(EventBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class EventCollaboratorBase(BaseModel):
    event_id: int
    organization_id: int


class EventCollaboratorCreate(BaseModel):
    organization_id: int


class EventCollaboratorResponse(EventCollaboratorBase):
    model_config = ConfigDict(from_attributes=True)


class EventBeneficiaryBase(BaseModel):
    event_id: int
    user_id: int
    benefit_time: datetime


class EventBeneficiaryCreate(BaseModel):
    user_id: int


class EventBeneficiaryResponse(EventBeneficiaryBase):
    model_config = ConfigDict(from_attributes=True)
