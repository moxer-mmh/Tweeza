# backend/app/schemas/user.py
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    phone: str
    full_name: str


class UserCreate(UserBase):
    password: str

    @field_validator("phone")
    def validate_phone(cls, v):
        if (
            not v.startswith("+2135")
            and not v.startswith("+2136")
            and not v.startswith("+2137")
        ):
            raise ValueError("Invalid Algerian mobile number")
        if len(v) != 13:
            raise ValueError("Invalid phone number length")
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class UserResponse(UserBase):
    id: int
    role: str
    last_login: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True
