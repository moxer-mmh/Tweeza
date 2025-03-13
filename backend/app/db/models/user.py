# backend/app/db/models/user.py
from sqlalchemy import Column, String, Integer, Float, DateTime, Enum
from sqlalchemy.orm import relationship, validates
from .base import Base, TimeStampMixin, UserRole
import re


class User(Base, TimeStampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(128), nullable=False)
    location = Column(String(128))
    latitude = Column(Float)
    longitude = Column(Float)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VOLUNTEER)
    last_login = Column(DateTime)

    # Role relationships (all optional)
    organizer_profile = relationship("Organizer", back_populates="user", uselist=False)
    volunteer_profile = relationship("Volunteer", back_populates="user", uselist=False)
    beneficiary_profile = relationship(
        "Beneficiary", back_populates="user", uselist=False
    )

    @validates("phone")
    def validate_phone(self, key, phone):
        if not re.match(r"^\+213[5-7]\d{8}$", phone):
            raise ValueError("Invalid Algerian phone number")
        return phone
