# backend/app/db/models/base.py
from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import validates
import enum

Base = declarative_base()


class TimeStampMixin:
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# Enums for consistent typing
class ResourceType(enum.Enum):
    FOOD = "Food"
    MONEY = "Money"
    MATERIALS = "Materials"
    VOLUNTEER_TIME = "Volunteer Time"


class EventType(enum.Enum):
    IFTAR = "Iftar"
    CLEANUP = "Cleanup"
    EMERGENCY = "Emergency"
    WORKSHOP = "Workshop"


class UserRole(enum.Enum):
    ORGANIZER = "organizer"
    VOLUNTEER = "volunteer"
    BENEFICIARY = "beneficiary"
    ADMIN = "admin"


class ParticipationStatus(enum.Enum):
    REGISTERED = "Registered"
    ATTENDED = "Attended"
    CANCELLED = "Cancelled"
    NO_SHOW = "No Show"
