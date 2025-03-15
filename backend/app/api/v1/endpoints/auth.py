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
    db: Session = Depends(get_db),
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

    Accepts either:
    - A Google/Facebook access token from an OAuth flow
    - A Google ID token (JWT) from Google Sign-In
    - A valid application token for re-authentication
    """
    try:
        # Log the OAuth login attempt
        print(f"Manual OAuth login attempt with provider: {oauth_data.provider}")

        # Validate the token format
        if not oauth_data.access_token or len(oauth_data.access_token) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid access token format",
            )

        # Log token info (safely)
        print(f"Token starts with: {oauth_data.access_token[:10]}...")
        print(f"Token length: {len(oauth_data.access_token)}")

        # Check if this is likely a JWT format token
        is_jwt = oauth_data.access_token.count(".") == 2
        if is_jwt:
            print("Detected JWT format token")

            # Check if it might be our own application token
            try:
                from app.core.security import decode_token

                payload = decode_token(oauth_data.access_token)
                if payload and "sub" in payload:
                    print(
                        f"Token appears to be a valid application token for user ID: {payload['sub']}"
                    )
                    # If it's a valid application token, we can just return a new token
                    user_id = int(payload["sub"])
                    return auth_service.create_user_token(user_id)
            except Exception as e:
                print(f"Error checking if token is an application token: {str(e)}")
                # Continue with normal OAuth flow if it's not our token

        # Get user info from OAuth provider
        user_info = oauth_service.get_oauth_user_info(
            oauth_data.provider, oauth_data.access_token
        )

        if not user_info:
            # If the token appears to be a JWT token but we failed to process it
            if is_jwt:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token format. Could not extract user information.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid OAuth credentials. Could not retrieve user information.",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        # Log successful user info retrieval
        print(f"Successfully retrieved user info for: {user_info.email}")

        # Authenticate or create user
        user = oauth_service.authenticate_oauth(db, user_info)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to authenticate via OAuth",
            )

        # Create access token
        return auth_service.create_user_token(user.id)
    except HTTPException as he:
        # Re-raise HTTP exceptions as-is
        raise he
    except Exception as e:
        print(f"Error in OAuth login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"OAuth authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# OAuth routes
@router.get("/google/login")
def google_login():
    """
    Generate Google OAuth login URL.
    """
    redirect_uri = "http://127.0.0.1:8000/api/v1/auth/google/callback"  # Match the URI configured in Google Console
    url = oauth_service.get_google_auth_url(redirect_uri)
    return {"url": url}


@router.get("/google/callback", response_model=Token)
def google_callback(code: str, db: Session = Depends(get_db)):
    """
    Handle Google OAuth callback.
    """
    try:
        redirect_uri = "http://127.0.0.1:8000/api/v1/auth/google/callback"

        # Validate the code format - basic checks
        if not code or len(code) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid authorization code format",
            )

        # Check if the code appears to be a JWT token (which won't work)
        if code.count(".") == 2 and len(code) < 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid authorization code format (looks like a JWT token)",
            )

        user, is_new = oauth_service.handle_google_callback(db, code, redirect_uri)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to authenticate with Google",
            )

        return auth_service.create_user_token(user.id)
    except ValueError as e:
        # Provide more detailed error information
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google authentication error: {str(e)}",
        )
    except Exception as e:
        # Log unexpected errors
        print(f"Unexpected error in Google callback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during authentication",
        )


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
