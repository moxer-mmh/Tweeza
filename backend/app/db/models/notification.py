# backend/app/db/models/notification.py
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimeStampMixin


class Notification(Base, TimeStampMixin):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(128), nullable=False)
    content = Column(Text)
    notification_type = Column(String(50))
    is_read = Column(Boolean, default=False)
    related_event_id = Column(Integer, ForeignKey("events.id", ondelete="SET NULL"))

    user = relationship("User")
    event = relationship("Event")
