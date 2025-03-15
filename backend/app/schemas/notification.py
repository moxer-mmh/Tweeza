from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from enum import Enum


class NotificationType(str, Enum):
    EVENT_INVITE = "event_invite"
    EVENT_UPDATE = "event_update"
    RESOURCE_REQUEST = "resource_request"
    RESOURCE_CONTRIBUTION = "resource_contribution"
    GENERAL = "general"


class NotificationBase(BaseModel):
    title: str
    message: str
    type: NotificationType
    reference_id: Optional[int] = None


class NotificationCreate(NotificationBase):
    recipient_id: int


class NotificationResponse(NotificationBase):
    id: int
    recipient_id: int
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
