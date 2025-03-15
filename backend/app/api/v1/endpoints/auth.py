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
    OAuthRequest,
    OAuthProvider,
    TwoFactorVerify,
)
from app.services import (
    auth_service,
    user_service,
    organization_service,
    oauth_service,
    two_factor_service,
)
from app.db import get_db
from app.db.models import User
from app.api.v1.dependencies import get_current_user  # Add this import

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


@router.post("/oauth/login", response_model=Token)
def oauth_login(*, oauth_data: OAuthRequest, db: Session = Depends(get_db)):
    """
    Login or register via OAuth provider.
    """
    # Get user info from OAuth provider
    user_info = oauth_service.get_oauth_user_info(
        oauth_data.provider, oauth_data.access_token
    )
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OAuth credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Authenticate or create user
    user = oauth_service.authenticate_oauth(db, user_info)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to authenticate via OAuth",
        )

    # Create access token
    return auth_service.create_user_token(user.id)


# OAuth routes
@router.get("/google/login")
def google_login():
    """
    Generate Google OAuth login URL.
    """
    redirect_uri = "http://localhost:3000/auth/google/callback"  # Use your actual frontend callback URL
    url = oauth_service.get_google_auth_url(redirect_uri)
    return {"url": url}


@router.get("/google/callback", response_model=Token)
def google_callback(code: str, db: Session = Depends(get_db)):
    """
    Handle Google OAuth callback.
    """
    user, is_new = oauth_service.handle_google_callback(db, code)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to authenticate with Google",
        )
    return auth_service.create_user_token(user.id)


@router.get("/facebook/login")
def facebook_login():
    """
    Generate Facebook OAuth login URL.
    """
    redirect_uri = "http://localhost:3000/auth/facebook/callback"  # Use your actual frontend callback URL
    url = oauth_service.get_facebook_auth_url(redirect_uri)
    return {"url": url}


@router.get("/facebook/callback", response_model=Token)
def facebook_callback(code: str, db: Session = Depends(get_db)):
    """
    Handle Facebook OAuth callback.
    """
    user, is_new = oauth_service.handle_facebook_callback(db, code)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to authenticate with Facebook",
        )
    return auth_service.create_user_token(user.id)


# Two-Factor Authentication routes
@router.post("/two-factor/enable")
def enable_two_factor(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Fix: use the imported function
):
    """
    Enable two-factor authentication.
    """
    method = data.get("method", "totp")
    phone_number = data.get("phone_number")

    success = two_factor_service.enable_two_factor(
        db, current_user.id, method, phone_number
    )

    return {"success": success}


@router.post("/two-factor/disable")
def disable_two_factor(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Fix: use the imported function
):
    """
    Disable two-factor authentication.
    """
    success = two_factor_service.disable_2fa(db, current_user.id)
    return {"success": success}


@router.post("/two-factor/send-code")
def send_verification_code(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Fix: use the imported function
):
    """
    Send verification code.
    """
    success = two_factor_service.send_verification_code(db, current_user.id)
    return {"success": success}


@router.post("/two-factor/verify")
def verify_two_factor_code(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Fix: use the imported function
):
    """
    Verify two-factor authentication code.
    """
    code = data.get("code")
    success = two_factor_service.verify_code(db, current_user.id, code)

    if success:
        # Generate token if verification is successful
        token = auth_service.create_user_token(current_user.id)
        return {
            "success": True,
            "access_token": token.access_token,
            "token_type": "bearer",
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid verification code",
    )


@router.get("/two-factor/status")
def get_two_factor_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Fix: use the imported function
):
    """
    Get the two-factor authentication status for the current user.
    """
    return two_factor_service.get_user_two_factor(db, current_user.id)
