# backend/app/db/models/event.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from ..base import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    title = Column(String(128), nullable=False)
    event_type = Column(String(50), nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    organization = relationship("Organization", back_populates="events")
    collaborators = relationship("EventCollaborator", back_populates="event")
    resource_requests = relationship("ResourceRequest", back_populates="event")
    beneficiaries = relationship("EventBeneficiary", back_populates="event")


class EventCollaborator(Base):
    __tablename__ = "event_collaborators"

    event_id = Column(Integer, ForeignKey("events.id"), primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), primary_key=True)

    event = relationship("Event", back_populates="collaborators")
    organization = relationship("Organization")
