from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from ..base import Base
from datetime import datetime


class Notification(Base):
    """Model for user notifications."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    notification_type = Column(
        String, default="general"
    )  # general, event, resource, system
    related_id = Column(Integer)  # ID of related entity (event, resource, etc.)
    related_type = Column(String)  # Type of related entity (event, resource, etc.)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    read_at = Column(DateTime, nullable=True)

    # Relationship
    user = relationship("User", back_populates="notifications")
