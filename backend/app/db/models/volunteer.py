# backend/app/db/models/volunteer.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimeStampMixin


class Volunteer(Base, TimeStampMixin):
    __tablename__ = "volunteers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    skills = relationship("VolunteerSkill", back_populates="volunteer")
    user = relationship("User", back_populates="volunteer_profile")
    contributions = relationship(
        "ResourceContribution", back_populates="volunteer", cascade="all, delete-orphan"
    )


class VolunteerSkill(Base):
    __tablename__ = "volunteer_skills"

    volunteer_id = Column(Integer, ForeignKey("volunteers.id"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), primary_key=True)
    level = Column(Integer)

    volunteer = relationship("Volunteer", back_populates="skills")
    skill = relationship("Skill", back_populates="volunteers")
