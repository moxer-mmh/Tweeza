from pydantic import BaseModel, ConfigDict
from typing import Optional
from .user import UserRoleEnum


class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class OrganizationResponse(OrganizationBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class OrganizationMemberBase(BaseModel):
    organization_id: int
    user_id: int
    role: UserRoleEnum


class OrganizationMemberCreate(BaseModel):
    user_id: int
    role: UserRoleEnum


class OrganizationMemberUpdate(BaseModel):
    role: Optional[UserRoleEnum] = None


class OrganizationMemberResponse(OrganizationMemberBase):
    model_config = ConfigDict(from_attributes=True)
