# backend/app/schemas/organization.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .user import UserResponse


class OrganizationBase(BaseModel):
    name: str
    org_type: str
    description: Optional[str] = None
    location: str
    latitude: float
    longitude: float


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationResponse(OrganizationBase):
    id: int
    verified: bool
    created_at: datetime
    members: list["UserResponse"] = []

    class Config:
        orm_mode = True
