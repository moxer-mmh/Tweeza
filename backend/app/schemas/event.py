from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class EventTypeEnum(str, Enum):
    IFTAR = "IFTAR"
    DONATION = "DONATION"
    VOLUNTEER = "VOLUNTEER"
    OTHER = "OTHER"


class EventBase(BaseModel):
    title: str
    event_type: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None


class EventCreate(EventBase):
    organization_id: int


class EventUpdate(BaseModel):
    title: Optional[str] = None
    event_type: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None


class EventResponse(EventBase):
    id: int
    organization_id: int

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class EventCollaboratorBase(BaseModel):
    event_id: int
    organization_id: int


class EventCollaboratorCreate(BaseModel):
    organization_id: int


class EventCollaboratorResponse(EventCollaboratorBase):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class EventBeneficiaryBase(BaseModel):
    event_id: int
    user_id: int
    benefit_time: datetime


class EventBeneficiaryCreate(BaseModel):
    user_id: int


class EventBeneficiaryResponse(EventBeneficiaryBase):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
