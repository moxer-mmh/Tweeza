# backend/app/db/models/user.py
from sqlalchemy import Column, String, Integer, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, UserRoleEnum


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(128), unique=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(128), nullable=False)
    location = Column(String(128))
    latitude = Column(Float)
    longitude = Column(Float)

    # Relationships
    roles = relationship(
        "UserRole", back_populates="user", cascade="all, delete-orphan"
    )
    organizations = relationship("OrganizationMember", back_populates="user")
    contributions = relationship("ResourceContribution", back_populates="user")
    benefited_events = relationship("EventBeneficiary", back_populates="user")

    def has_role(self, role: UserRoleEnum) -> bool:
        return any(r.role == role for r in self.roles)


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role = Column(Enum(UserRoleEnum), primary_key=True)
    user = relationship("User", back_populates="roles")
