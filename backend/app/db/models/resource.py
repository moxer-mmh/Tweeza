# backend/app/db/models/resource.py
from sqlalchemy import Column, Integer, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base, ResourceTypeEnum


class ResourceRequest(Base):
    __tablename__ = "resource_requests"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    resource_type = Column(Enum(ResourceTypeEnum))
    quantity_needed = Column(Integer)
    quantity_received = Column(Integer, default=0)

    event = relationship("Event", back_populates="resource_requests")
    contributions = relationship("ResourceContribution", back_populates="request")


class ResourceContribution(Base):
    __tablename__ = "resource_contributions"

    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey("resource_requests.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    quantity = Column(Integer)
    contribution_time = Column(DateTime, server_default=func.now())

    request = relationship("ResourceRequest", back_populates="contributions")
    user = relationship("User", back_populates="contributions")
