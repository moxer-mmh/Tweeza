from sqlalchemy.orm import Session
from typing import Optional
from app.db.models import User
from app.core.security import verify_password, create_access_token
from app.schemas import Token, UserLogin, UserRoleEnum
from datetime import timedelta
from app.core.config import settings
from app.services import user_service


def authenticate_user(db: Session, auth_data: UserLogin) -> Optional[User]:
    """Authenticate a user with email and password."""
    user = user_service.get_user_by_email(db, auth_data.email)

    if not user:
        return None

    if not verify_password(auth_data.password, user.password_hash):
        return None

    return user


def create_user_token(user_id: int) -> Token:
    """Create an access token for the user."""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user_id, expires_delta=access_token_expires
    )
    return Token(access_token=access_token)


def check_user_role(user: User, required_role: UserRoleEnum) -> bool:
    """Check if the user has a specific role."""
    return user.has_role(required_role)
