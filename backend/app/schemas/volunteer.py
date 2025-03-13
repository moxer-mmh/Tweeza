# backend/app/schemas/volunteer.py
from pydantic import BaseModel
from .user import UserResponse


class VolunteerSkillBase(BaseModel):
    skill_id: int
    level: int


class VolunteerResponse(BaseModel):
    id: int
    user: UserResponse
    skills: list[VolunteerSkillBase] = []

    class Config:
        orm_mode = True
