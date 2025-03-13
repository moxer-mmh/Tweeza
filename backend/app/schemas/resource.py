# backend/app/schemas/resource.py
from pydantic import BaseModel


class ResourceRequestBase(BaseModel):
    resource_type: str
    quantity_needed: int
    urgency_level: int


class ResourceRequestCreate(ResourceRequestBase):
    pass


class ResourceContribution(BaseModel):
    quantity: int
    delivery_confirmed: bool = False


class ResourceResponse(ResourceRequestBase):
    id: int
    quantity_received: int
    contributions: list[ResourceContribution] = []

    class Config:
        orm_mode = True
