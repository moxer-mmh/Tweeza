# backend/app/db/models/skill.py
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from .base import Base


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    description = Column(Text)

    volunteers = relationship("VolunteerSkill", back_populates="skill")
