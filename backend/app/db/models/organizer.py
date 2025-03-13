# backend/app/db/models/organizer.py
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Text, Float, Index
from sqlalchemy.orm import relationship
from .base import Base, TimeStampMixin


class Organizer(Base, TimeStampMixin):
    __tablename__ = "organizers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    organization_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="SET NULL")
    )
    role = Column(String(50))  # Manager, Coordinator, etc.

    user = relationship("User", back_populates="organizer_profile")
    organization = relationship("Organization", back_populates="organizers")


class Organization(Base, TimeStampMixin):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    org_type = Column(String(50), nullable=False)
    description = Column(Text)
    location = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    verified = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"))

    organizers = relationship("Organizer", back_populates="organization")
    events = relationship("Event", back_populates="organization")
    members = relationship("OrganizationMember", back_populates="organization")

    __table_args__ = (Index("idx_org_location", "latitude", "longitude"),)


class OrganizationMember(Base):
    __tablename__ = "organization_members"

    organization_id = Column(Integer, ForeignKey("organizations.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role = Column(String(50))

    organization = relationship("Organization", back_populates="members")
    user = relationship("User")
