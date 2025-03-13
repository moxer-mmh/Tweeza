# backend/app/db/models/resource.py
from sqlalchemy import Column, Integer, Enum, ForeignKey, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base, TimeStampMixin, ResourceType


class ResourceRequest(Base, TimeStampMixin):
    __tablename__ = "resource_requests"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"))
    resource_type = Column(Enum(ResourceType), nullable=False)
    quantity_needed = Column(Integer)
    quantity_received = Column(Integer, default=0)
    urgency_level = Column(Integer)  # 1-5 scale

    event = relationship("Event", back_populates="resources")
    contributions = relationship("ResourceContribution", back_populates="request")


class ResourceContribution(Base):
    __tablename__ = "resource_contributions"

    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey("resource_requests.id"))
    volunteer_id = Column(Integer, ForeignKey("volunteers.id"))
    quantity = Column(Integer)
    contribution_date = Column(DateTime, server_default=func.now())
    delivery_confirmed = Column(Boolean, default=False)
    confirmed_by = Column(Integer, ForeignKey("organizers.id"))

    request = relationship("ResourceRequest", back_populates="contributions")
    volunteer = relationship("Volunteer", back_populates="contributions")
