from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


class ResourceTypeEnum(str, Enum):
    FOOD = "food"
    MONEY = "money"
    MATERIALS = "materials"
    TIME = "time"


class ResourceRequestBase(BaseModel):
    event_id: int
    resource_type: ResourceTypeEnum
    quantity_needed: int
    quantity_received: int = 0


class ResourceRequestCreate(BaseModel):
    resource_type: ResourceTypeEnum
    quantity_needed: int


class ResourceRequestUpdate(BaseModel):
    resource_type: Optional[ResourceTypeEnum] = None
    quantity_needed: Optional[int] = None
    quantity_received: Optional[int] = None


class ResourceRequestResponse(ResourceRequestBase):
    id: int

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class ResourceContributionBase(BaseModel):
    request_id: int
    user_id: int
    quantity: int
    contribution_time: datetime


class ResourceContributionCreate(BaseModel):
    request_id: int
    quantity: int


class ResourceContributionUpdate(BaseModel):
    quantity: Optional[int] = None


class ResourceContributionResponse(ResourceContributionBase):
    id: int

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
