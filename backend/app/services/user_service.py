from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models import User, UserRole
from app.schemas import UserCreate, UserUpdate, UserRoleEnum
from app.core.security import get_password_hash, verify_password


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
    """Get a user by phone number."""
    return db.query(User).filter(User.phone == phone).first()


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user."""
    # Check if user exists
    if get_user_by_email(db, user_data.email):
        raise ValueError("Email already registered")

    if get_user_by_phone(db, user_data.phone):
        raise ValueError("Phone number already registered")

    # Create user object
    db_user = User(
        email=user_data.email,
        phone=user_data.phone,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        location=user_data.location,
        latitude=user_data.latitude,
        longitude=user_data.longitude,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Add roles
    for role in user_data.roles:
        user_role = UserRole(user_id=db_user.id, role=role)
        db.add(user_role)

    db.commit()
    db.refresh(db_user)

    return db_user


def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
    """Update an existing user."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    # Update fields if provided
    update_data = user_data.model_dump(exclude_unset=True)

    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user."""
    db_user = get_user(db, user_id)
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()
    return True


def add_role_to_user(
    db: Session, user_id: int, role: UserRoleEnum
) -> Optional[UserRole]:
    """Add a role to a user."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    # Check if role already exists
    existing_role = (
        db.query(UserRole)
        .filter(UserRole.user_id == user_id, UserRole.role == role)
        .first()
    )

    if existing_role:
        return existing_role

    # Add new role
    user_role = UserRole(user_id=user_id, role=role)
    db.add(user_role)
    db.commit()
    return user_role


def remove_role_from_user(db: Session, user_id: int, role: UserRoleEnum) -> bool:
    """Remove a role from a user."""
    db_role = (
        db.query(UserRole)
        .filter(UserRole.user_id == user_id, UserRole.role == role)
        .first()
    )

    if not db_role:
        return False

    db.delete(db_role)
    db.commit()
    return True
