from typing import Optional
from datetime import datetime
from pydantic import BaseModel
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

    class Config:
        orm_mode = True
