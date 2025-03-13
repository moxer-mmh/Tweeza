# backend/app/db/models/beneficiary.py
from sqlalchemy import Column, Integer, ForeignKey, Text, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base, TimeStampMixin


class Beneficiary(Base, TimeStampMixin):
    __tablename__ = "beneficiaries"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    needs = Column(Text)  # Specific needs description
    assistance_history = relationship("AssistanceRecord", back_populates="beneficiary")

    user = relationship("User", back_populates="beneficiary_profile")


class AssistanceRecord(Base, TimeStampMixin):
    __tablename__ = "assistance_records"

    id = Column(Integer, primary_key=True)
    assistance_date = Column(DateTime, server_default=func.now())
    beneficiary_id = Column(Integer, ForeignKey("beneficiaries.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    assistance_type = Column(String(50))

    beneficiary = relationship("Beneficiary", back_populates="assistance_history")
    event = relationship("Event")
