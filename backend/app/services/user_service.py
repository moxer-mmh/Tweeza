from typing import List, Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime

from app.db import User
from app.schemas import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get multiple users with pagination."""
        return self.db.query(User).offset(skip).limit(limit).all()

    def create_user(self, user_in: UserCreate) -> User:
        """Create a new user."""
        # Check for existing user with same email
        if self.get_user_by_email(user_in.email):
            raise ValueError("Email already registered")

        # Create user with hashed password
        db_user = User(
            email=user_in.email,
            phone=user_in.phone,
            full_name=user_in.full_name,
            password_hash=get_password_hash(user_in.password),
            role="volunteer",  # Default role
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_user(self, user_id: int, user_in: UserUpdate) -> Optional[User]:
        """Update user information."""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None

        # Update user attributes that are provided
        update_data = user_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def record_login(self, user_id: int) -> None:
        """Record user login time."""
        db_user = self.get_user_by_id(user_id)
        if db_user:
            db_user.last_login = datetime.utcnow()
            self.db.commit()
