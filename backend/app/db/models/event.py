# backend/app/db/models/event.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Enum,
    Float,
    Boolean,
    Index,
)
from sqlalchemy.orm import relationship
from .base import Base, TimeStampMixin, EventType, ParticipationStatus


class Event(Base, TimeStampMixin):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    title = Column(String(128), nullable=False)
    event_type = Column(Enum(EventType), nullable=False)
    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),  # Changed from SET NULL
        nullable=False,
    )
    location = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    is_emergency = Column(Boolean, default=False)
    emergency_contact = Column(String(20))

    organization = relationship("Organization", back_populates="events")
    participants = relationship("EventParticipant", back_populates="event")
    resources = relationship("ResourceRequest", back_populates="event")
    gallery = relationship("EventGallery", back_populates="event")

    __table_args__ = (
        Index("idx_event_location", "latitude", "longitude"),
        Index("idx_event_type", "event_type"),
    )


class EventParticipant(Base):
    __tablename__ = "event_participants"

    event_id = Column(Integer, ForeignKey("events.id"), primary_key=True)
    volunteer_id = Column(Integer, ForeignKey("volunteers.id"), primary_key=True)
    status = Column(String(20))  # Registered, Attended, Cancelled
    status = Column(Enum(ParticipationStatus), default=ParticipationStatus.REGISTERED)

    event = relationship("Event", back_populates="participants")
    volunteer = relationship("Volunteer")


class EventGallery(Base):
    __tablename__ = "event_gallery"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"))
    image_url = Column(String(255), nullable=False)
    caption = Column(String(256))

    event = relationship("Event", back_populates="gallery")
