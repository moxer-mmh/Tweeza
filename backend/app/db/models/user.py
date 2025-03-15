# backend/app/db/models/user.py
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ..base import Base


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
    two_factor_secret = Column(String, nullable=True)
    two_factor_enabled = Column(Boolean, default=False)

    # Relationships
    roles = relationship(
        "UserRole", back_populates="user", cascade="all, delete-orphan"
    )
    organizations = relationship("OrganizationMember", back_populates="user")
    contributions = relationship("ResourceContribution", back_populates="user")
    benefited_events = relationship("EventBeneficiary", back_populates="user")
    oauth_connections = relationship(
        "OAuthConnection", back_populates="user", cascade="all, delete-orphan"
    )
    notifications = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )

    def has_role(self, role):
        role_value = role.value if hasattr(role, "value") else role
        return any(r.role == role_value for r in self.roles)


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role = Column(String(50), primary_key=True)
    user = relationship("User", back_populates="roles")
