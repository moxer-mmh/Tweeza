# backend/app/schemas/beneficiary.py
from pydantic import BaseModel
from datetime import datetime
from .user import UserResponse


class AssistanceRecord(BaseModel):
    event_id: int
    assistance_type: str
    assistance_date: datetime


class BeneficiaryResponse(BaseModel):
    id: int
    user: UserResponse
    needs: str
    assistance_history: list[AssistanceRecord] = []

    class Config:
        orm_mode = True
