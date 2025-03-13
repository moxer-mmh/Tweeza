# backend/app/schemas/notification.py
from pydantic import BaseModel
from datetime import datetime


class NotificationBase(BaseModel):
    title: str
    content: str
    notification_type: str


class NotificationResponse(NotificationBase):
    id: int
    created_at: datetime
    is_read: bool

    class Config:
        orm_mode = True
