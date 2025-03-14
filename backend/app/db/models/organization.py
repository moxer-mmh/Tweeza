# backend/app/db/models/organization.py
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Text, Float
from sqlalchemy.orm import relationship
from .base import Base, UserRoleEnum


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False)
    description = Column(Text)
    location = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)

    members = relationship("OrganizationMember", back_populates="organization")
    events = relationship("Event", back_populates="organization")


class OrganizationMember(Base):
    __tablename__ = "organization_members"

    organization_id = Column(Integer, ForeignKey("organizations.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role = Column(Enum(UserRoleEnum))

    organization = relationship("Organization", back_populates="members")
    user = relationship("User", back_populates="organizations")
