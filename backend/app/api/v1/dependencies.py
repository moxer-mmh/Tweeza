from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app.db import get_db, User
from app.core.security import decode_token
from app.services import user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        if payload is None:
            raise credentials_exception

        user_id = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except (JWTError, ValueError):
        raise credentials_exception

    user = user_service.get_user(db, user_id)
    if user is None:
        raise credentials_exception

    return user
