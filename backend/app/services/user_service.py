from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.models import User
from app.schemas import UserCreate, UserUpdate
from app.core import get_password_hash


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def create_user(self, user_in: UserCreate) -> User:
        # Check if user already exists
        db_user = self.get_user_by_email(self.db, user_in.email)
        if db_user:
            raise ValueError("Email already registered")

        # Create new user
        db_user = User(
            username=user_in.username,
            email=user_in.email,
            full_name=user_in.full_name,
            bio=user_in.bio,
            location=user_in.location,
            latitude=user_in.latitude,
            longitude=user_in.longitude,
            phone_number=user_in.phone_number,
            password_hash=get_password_hash(user_in.password),
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
