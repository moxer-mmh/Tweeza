from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas import Token, UserLogin, UserCreate, UserResponse
from app.services import auth_service, user_service
from app.db import get_db

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    auth_data = UserLogin(email=form_data.username, password=form_data.password)
    user = auth_service.authenticate_user(db, auth_data)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return auth_service.create_user_token(user.id)


@router.post("/register", response_model=UserResponse)
def register(*, user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    try:
        user = user_service.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
