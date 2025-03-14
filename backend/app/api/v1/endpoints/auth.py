from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas import (
    Token,
    UserLogin,
    UserCreate,
    UserResponse,
    UserRoleEnum,
    OrganizationCreate,
)
from app.services import auth_service, user_service, organization_service
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
    # Only allow WORKER, VOLUNTEER, or BENEFICIARY roles
    allowed_roles = [
        UserRoleEnum.WORKER,
        UserRoleEnum.VOLUNTEER,
        UserRoleEnum.BENEFICIARY,
    ]

    # Ensure user only selects allowed roles
    if not user_data.roles:
        # Default to beneficiary if no role is selected
        user_data.roles = [UserRoleEnum.BENEFICIARY]
    elif any(role not in allowed_roles for role in user_data.roles):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Regular users can only register as worker, volunteer, or beneficiary",
        )

    try:
        user = user_service.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/register-organization", response_model=UserResponse)
def register_organization(
    *,
    user_data: UserCreate,
    organization_data: OrganizationCreate,
    db: Session = Depends(get_db)
):
    """
    Register as an organization owner (admin).
    Creates both a user account and an organization with the user as admin.
    """
    # Force the user role to be only admin - ignore any provided roles
    user_data.roles = []  # Clear any roles the user might have submitted

    try:
        # First, create the user
        user = user_service.create_user(db, user_data)

        # Then, create the organization with this user as admin
        organization_service.create_organization(db, organization_data, user.id)

        # Refresh the user to include the new role
        updated_user = user_service.get_user(db, user.id)
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
