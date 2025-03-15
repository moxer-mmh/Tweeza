# backend/app/db/models/beneficiary.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..base import Base


class EventBeneficiary(Base):
    __tablename__ = "event_beneficiaries"

    event_id = Column(Integer, ForeignKey("events.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    benefit_time = Column(DateTime, server_default=func.now())

    event = relationship("Event", back_populates="beneficiaries")
    user = relationship("User", back_populates="benefited_events")
