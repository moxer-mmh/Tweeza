from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from enum import Enum


class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    WORKER = "worker"
    VOLUNTEER = "volunteer"
    BENEFICIARY = "beneficiary"


class UserRoleCreate(BaseModel):
    role: UserRoleEnum


class UserRoleResponse(BaseModel):
    role: UserRoleEnum

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class UserBase(BaseModel):
    email: EmailStr
    phone: str
    full_name: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class UserCreate(UserBase):
    password: str
    roles: List[UserRoleEnum] = []


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    roles: List[UserRoleResponse] = []

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str
