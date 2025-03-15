from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.db.models import User, OAuthConnection
from app.schemas import OAuthUserInfo, OAuthProvider, UserCreate
from app.services import user_service, auth_service
from app.core.config import settings
import requests
from datetime import datetime, timedelta


class OAuthProviderConfig:
    """Configuration for OAuth providers"""

    CONFIGS = {
        OAuthProvider.GOOGLE: {
            "user_info_url": "https://www.googleapis.com/oauth2/v3/userinfo",
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
        },
        OAuthProvider.FACEBOOK: {
            "user_info_url": "https://graph.facebook.com/me?fields=id,name,email,picture",
            "client_id": settings.FACEBOOK_CLIENT_ID,
            "client_secret": settings.FACEBOOK_CLIENT_SECRET,
        },
        # Add other providers as needed
    }


def get_oauth_user_info(
    provider: OAuthProvider, access_token: str
) -> Optional[OAuthUserInfo]:
    """Get user information from OAuth provider."""
    if provider not in OAuthProviderConfig.CONFIGS:
        return None

    config = OAuthProviderConfig.CONFIGS[provider]
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(config["user_info_url"], headers=headers)
        response.raise_for_status()
        user_data = response.json()

        # Extract data based on provider
        if provider == OAuthProvider.GOOGLE:
            return OAuthUserInfo(
                provider=provider,
                provider_user_id=user_data["sub"],
                email=user_data["email"],
                full_name=user_data.get("name"),
                profile_picture=user_data.get("picture"),
                raw_data=user_data,
            )
        elif provider == OAuthProvider.FACEBOOK:
            return OAuthUserInfo(
                provider=provider,
                provider_user_id=user_data["id"],
                email=user_data["email"],
                full_name=user_data.get("name"),
                profile_picture=user_data.get("picture", {}).get("data", {}).get("url"),
                raw_data=user_data,
            )
    except Exception as e:
        print(f"Error getting OAuth user info: {str(e)}")
        return None

    return None


def get_user_by_oauth(
    db: Session, provider: OAuthProvider, provider_user_id: str
) -> Optional[User]:
    """Get user by OAuth provider and provider user ID."""
    oauth_connection = (
        db.query(OAuthConnection)
        .filter(
            OAuthConnection.provider == provider,
            OAuthConnection.provider_user_id == provider_user_id,
        )
        .first()
    )

    if oauth_connection:
        return oauth_connection.user
    return None


def create_oauth_connection(
    db: Session, user_id: int, oauth_info: OAuthUserInfo, tokens: Dict[str, Any] = None
) -> OAuthConnection:
    """Create or update OAuth connection for a user."""
    # Check if connection already exists
    existing = (
        db.query(OAuthConnection)
        .filter(
            OAuthConnection.user_id == user_id,
            OAuthConnection.provider == oauth_info.provider,
            OAuthConnection.provider_user_id == oauth_info.provider_user_id,
        )
        .first()
    )

    if existing:
        # Update existing connection
        if tokens:
            existing.access_token = tokens.get("access_token")
            existing.refresh_token = tokens.get("refresh_token")
            existing.expires_at = int(
                datetime.now().timestamp() + tokens.get("expires_in", 3600)
            )
        db.commit()
        return existing

    # Create new connection
    oauth_connection = OAuthConnection(
        user_id=user_id,
        provider=oauth_info.provider,
        provider_user_id=oauth_info.provider_user_id,
        access_token=tokens.get("access_token") if tokens else None,
        refresh_token=tokens.get("refresh_token") if tokens else None,
        expires_at=(
            int(datetime.now().timestamp() + tokens.get("expires_in", 3600))
            if tokens
            else None
        ),
    )

    db.add(oauth_connection)
    db.commit()
    db.refresh(oauth_connection)
    return oauth_connection


def authenticate_oauth(db: Session, oauth_info: OAuthUserInfo) -> Optional[User]:
    """Authenticate user with OAuth or create a new user if not exists."""
    # Try to find existing OAuth connection
    user = get_user_by_oauth(db, oauth_info.provider, oauth_info.provider_user_id)

    if user:
        return user

    # Try to find user by email
    user = user_service.get_user_by_email(db, oauth_info.email)

    if not user:
        # Create new user
        # Generate a random secure password for OAuth users
        import secrets
        import string

        password = "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(20)
        )

        user_data = UserCreate(
            email=oauth_info.email,
            password=password,
            full_name=oauth_info.full_name or oauth_info.email.split("@")[0],
            phone="",  # Placeholder, might be updated later
            roles=[],  # Default roles will be assigned
            location="",
            latitude=0.0,
            longitude=0.0,
        )

        user = user_service.create_user(db, user_data)

    # Create the OAuth connection for this user
    create_oauth_connection(db, user.id, oauth_info)

    return user


from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, Tuple
from app.db.models import User, OAuthConnection
from app.schemas import OAuthProvider, UserCreate
from datetime import datetime


# These would be properly initialized in a real application
# using values from environment variables or configuration
class GoogleOAuthClient:
    def get_authorization_url(self, redirect_uri: str) -> str:
        # In a real implementation, this would generate a proper OAuth URL
        return (
            "https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri="
            + redirect_uri
        )

    def get_user_info(self, code: str) -> Dict[str, Any]:
        # In a real implementation, this would exchange the code for tokens
        # and fetch user info from Google
        return {
            "id": "google123",
            "email": "google_user@example.com",
            "name": "Google User",
            "picture": "https://example.com/avatar.jpg",
        }


class FacebookOAuthClient:
    def get_authorization_url(self, redirect_uri: str) -> str:
        # In a real implementation, this would generate a proper OAuth URL
        return (
            "https://www.facebook.com/dialog/oauth?client_id=YOUR_CLIENT_ID&redirect_uri="
            + redirect_uri
        )

    def get_user_info(self, code: str) -> Dict[str, Any]:
        # In a real implementation, this would exchange the code for tokens
        # and fetch user info from Facebook
        return {
            "id": "fb123",
            "email": "facebook_user@example.com",
            "name": "Facebook User",
            "picture": {"data": {"url": "https://example.com/fb_avatar.jpg"}},
        }


# Initialize OAuth clients
google_client = GoogleOAuthClient()
facebook_client = FacebookOAuthClient()


def get_google_auth_url(redirect_uri: str) -> str:
    """
    Generate Google OAuth authorization URL.
    """
    return google_client.get_authorization_url(redirect_uri)


def handle_google_callback(db: Session, code: str) -> Tuple[User, bool]:
    """
    Handle Google OAuth callback, creating or retrieving the user.
    Returns (user, is_new_user) tuple.
    """
    # Get user info from Google
    user_info = google_client.get_user_info(code)

    # Create or update user from OAuth data
    return create_or_update_user_from_oauth(db, user_info, OAuthProvider.GOOGLE)


def get_facebook_auth_url(redirect_uri: str) -> str:
    """
    Generate Facebook OAuth authorization URL.
    """
    return facebook_client.get_authorization_url(redirect_uri)


def handle_facebook_callback(db: Session, code: str) -> Tuple[User, bool]:
    """
    Handle Facebook OAuth callback, creating or retrieving the user.
    Returns (user, is_new_user) tuple.
    """
    # Get user info from Facebook
    user_info = facebook_client.get_user_info(code)

    # Create or update user from OAuth data
    return create_or_update_user_from_oauth(db, user_info, OAuthProvider.FACEBOOK)


def create_or_update_user_from_oauth(
    db: Session, user_info: Dict[str, Any], provider: OAuthProvider
) -> Tuple[User, bool]:
    """
    Create a new user or update existing one based on OAuth data.
    Returns (user, is_new_user) tuple.
    """
    # Normalize emails to lowercase
    email = user_info.get("email", "").lower()

    # Get provider-specific ID
    provider_id = user_info.get("id")

    # Check if user exists with this provider ID
    oauth_connection = (
        db.query(OAuthConnection)
        .filter(
            OAuthConnection.provider == provider.value,
            OAuthConnection.provider_user_id == provider_id,
        )
        .first()
    )

    # If OAuth account exists, return the associated user
    if oauth_connection:
        user = db.query(User).filter(User.id == oauth_connection.user_id).first()
        return user, False

    # Check if user exists with this email
    user = db.query(User).filter(User.email == email).first()
    is_new = False

    if not user:
        # Create new user
        name = user_info.get("name", "")
        picture_url = (
            user_info.get("picture", {}).get("data", {}).get("url")
            if isinstance(user_info.get("picture"), dict)
            else user_info.get("picture")
        )

        # Create user without created_at field
        user = User(
            email=email,
            full_name=name,
            password_hash="oauth_user",  # Set a placeholder password
            phone="oauth_user",  # Set a placeholder phone
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        is_new = True

    # Create OAuth account link if it doesn't exist
    provider_field = f"{provider.value.lower()}_id"
    if hasattr(user, provider_field):
        setattr(user, provider_field, provider_id)

    # Create an OAuth connection record
    oauth_connection = OAuthConnection(
        user_id=user.id,
        provider=provider.value,
        provider_user_id=provider_id,
        access_token="",  # In a real app, you'd store the access token
        expires_at=None,  # In a real app, you'd calculate expiry
    )
    db.add(oauth_connection)
    db.commit()

    return user, is_new
