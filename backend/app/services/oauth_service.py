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
        print(f"Unsupported OAuth provider: {provider}")
        return None

    config = OAuthProviderConfig.CONFIGS[provider]

    print(f"Fetching user info from {provider} using access token")

    # Check if the token is a JWT (ID token) from Google
    if provider == OAuthProvider.GOOGLE and access_token.count(".") == 2:
        print("Detected Google ID token (JWT format)")
        return extract_google_info_from_id_token(access_token)

    # Check if token might have a "Bearer" prefix already
    if access_token.startswith("Bearer "):
        # Extract the token part
        print("Token already has Bearer prefix, extracting token...")
        actual_token = access_token[7:]
    else:
        actual_token = access_token

    print(f"Token length: {len(actual_token)}")

    # Different providers might need different header formats
    headers = {}

    if provider == OAuthProvider.GOOGLE:
        # Google OAuth access tokens typically start with "ya29."
        if not actual_token.startswith("ya29."):
            print(
                "Warning: Token doesn't match expected format for Google OAuth access token"
            )

        headers = {"Authorization": f"Bearer {actual_token}"}
        user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    else:
        # For other providers like Facebook, the token might be sent as a query parameter
        headers = {"Authorization": f"Bearer {actual_token}"}
        user_info_url = config["user_info_url"]

    print(f"Making request to: {user_info_url}")
    print(f"Using authorization header: Bearer {actual_token[:10]}...")

    # For providers that use query parameters instead of headers
    params = {}
    if provider == OAuthProvider.FACEBOOK:
        params = {"access_token": actual_token}

    try:
        response = requests.get(user_info_url, headers=headers, params=params)

        # Log response details
        print(f"User info response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error response body: {response.text}")
        else:
            print("Successfully received user info response")

        response.raise_for_status()
        user_data = response.json()

        # Debug the response
        print(f"User data keys: {list(user_data.keys())}")
        print(
            f"Retrieved user data: email={user_data.get('email', 'N/A')}, name={user_data.get('name', user_data.get('given_name', 'N/A'))}"
        )

        # Extract data based on provider
        if provider == OAuthProvider.GOOGLE:
            # Check if we have the expected data
            if "sub" not in user_data:
                print(
                    f"Warning: 'sub' field missing from Google response. Available fields: {list(user_data.keys())}"
                )
                # Try to use a different ID field if sub is missing
                provider_user_id = (
                    user_data.get("sub")
                    or user_data.get("id")
                    or user_data.get("user_id")
                )
                if not provider_user_id:
                    print("Error: Could not determine user ID from Google response")
                    return None
            else:
                provider_user_id = user_data["sub"]

            # Check for email
            if "email" not in user_data:
                print(f"Warning: 'email' field missing from Google response.")
                return None

            return OAuthUserInfo(
                provider=provider,
                provider_user_id=provider_user_id,
                email=user_data["email"],
                full_name=user_data.get("name"),
                profile_picture=user_data.get("picture"),
                raw_data=user_data,
            )
        elif provider == OAuthProvider.FACEBOOK:
            # Similar validation for Facebook data
            if "id" not in user_data or "email" not in user_data:
                print(
                    f"Warning: Required fields missing from Facebook response. Available fields: {list(user_data.keys())}"
                )
                return None

            return OAuthUserInfo(
                provider=provider,
                provider_user_id=user_data["id"],
                email=user_data["email"],
                full_name=user_data["name"],
                profile_picture=user_data.get("picture", {}).get("data", {}).get("url"),
                raw_data=user_data,
            )
    except requests.RequestException as e:
        print(f"Request error getting OAuth user info: {str(e)}")
        return None
    except ValueError as e:
        print(f"Value error parsing OAuth response: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error getting OAuth user info: {str(e)}")
        return None

    return None


def extract_google_info_from_id_token(id_token: str) -> Optional[OAuthUserInfo]:
    """
    Extract user information from a Google ID token (JWT format) or application token
    """
    try:
        # Simple JWT parsing (in production, use a proper JWT library with verification)
        parts = id_token.split(".")
        if len(parts) != 3:
            print("Invalid JWT format (should have 3 parts)")
            return None

        # Parse the payload (middle part)
        import base64
        import json

        # Decode payload (might need padding)
        payload = parts[1]
        payload += "=" * (4 - len(payload) % 4) if len(payload) % 4 else ""

        try:
            decoded = base64.urlsafe_b64decode(payload)
            user_data = json.loads(decoded)
            print(f"Decoded JWT payload: {user_data}")
        except Exception as e:
            print(f"Error decoding JWT payload: {str(e)}")
            return None

        # Check if this is our own application token
        if set(user_data.keys()) == {"exp", "sub"} or set(user_data.keys()) == {
            "sub",
            "exp",
        }:
            print(
                "Detected internal application token - will lookup user from database"
            )
            # This appears to be our internal token, get user from database
            from app.services import auth_service

            try:
                user_id = int(user_data["sub"])
                print(f"Looking up user with ID: {user_id}")

                # Get user from database
                from app.db import get_db
                from app.services import user_service

                db = next(get_db())
                user = user_service.get_user(db, user_id)

                if not user:
                    print(f"User not found with ID: {user_id}")
                    return None

                print(f"Found user: {user.email}")

                return OAuthUserInfo(
                    provider=OAuthProvider.GOOGLE,  # We're defaulting to Google here
                    provider_user_id=str(user_id),
                    email=user.email,
                    full_name=user.full_name,
                    profile_picture=None,  # We don't have this info from our DB
                    raw_data={"sub": str(user_id), "email": user.email},
                )
            except Exception as e:
                print(f"Error looking up user from token: {str(e)}")
                return None

        # Check for standard ID token fields
        if "sub" not in user_data:
            print(
                f"Missing 'sub' field in token. Available fields: {list(user_data.keys())}"
            )
            return None

        # For Google ID tokens, email should be present
        # For other tokens, we might have it or we might have looked it up from the database
        if "email" not in user_data:
            print(
                f"Missing 'email' field in token. Available fields: {list(user_data.keys())}"
            )

            # Try to get user info from sub if possible
            try:
                from app.db import get_db
                from app.services import user_service

                db = next(get_db())
                # Check if it's a string that could be a Google user ID
                if isinstance(user_data["sub"], str) and len(user_data["sub"]) > 10:
                    # Try to find user with this Google ID
                    oauth_conn = (
                        db.query(OAuthConnection)
                        .filter(
                            OAuthConnection.provider == OAuthProvider.GOOGLE.value,
                            OAuthConnection.provider_user_id == user_data["sub"],
                        )
                        .first()
                    )
                    if oauth_conn:
                        user = oauth_conn.user
                        print(f"Found user via OAuth connection: {user.email}")
                        user_data["email"] = user.email
                    else:
                        print(f"No OAuth connection found for sub: {user_data['sub']}")
                        return None
                else:
                    # Try to interpret as user ID
                    try:
                        user_id = int(user_data["sub"])
                        user = user_service.get_user(db, user_id)
                        if user:
                            print(f"Found user by ID: {user.email}")
                            user_data["email"] = user.email
                        else:
                            print(f"No user found with ID: {user_id}")
                            return None
                    except (ValueError, TypeError):
                        print(f"Could not interpret sub as user ID: {user_data['sub']}")
                        return None
            except Exception as e:
                print(f"Error looking up user by sub: {str(e)}")
                return None

        print(f"Successfully extracted user info from token: {user_data.get('email')}")

        return OAuthUserInfo(
            provider=OAuthProvider.GOOGLE,  # Default to Google
            provider_user_id=user_data["sub"],
            email=user_data["email"],
            full_name=user_data.get("name"),
            profile_picture=user_data.get("picture"),
            raw_data=user_data,
        )
    except Exception as e:
        print(f"Error processing token: {str(e)}")
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
    def __init__(self):
        # Add debug print statements to verify configuration
        print(f"Google OAuth Client Configuration:")
        print(
            f"Client ID: {settings.GOOGLE_CLIENT_ID[:15]}..."
            if settings.GOOGLE_CLIENT_ID
            else "Not set"
        )

        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise ValueError(
                "Google OAuth credentials are not properly configured in environment variables"
            )

        # Verify format - client ID should typically end with .apps.googleusercontent.com
        if not str(settings.GOOGLE_CLIENT_ID).endswith(".apps.googleusercontent.com"):
            print(
                "WARNING: Your Google client ID doesn't match the expected format (should end with .apps.googleusercontent.com)"
            )

        # Verify client secret format - should start with GOCSPX- typically
        if settings.GOOGLE_CLIENT_SECRET and not str(
            settings.GOOGLE_CLIENT_SECRET
        ).startswith("GOCSPX-"):
            print(
                "WARNING: Your Google client secret doesn't match the expected format (should start with GOCSPX-)"
            )

        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.auth_uri = "https://accounts.google.com/o/oauth2/auth"
        self.token_uri = "https://oauth2.googleapis.com/token"
        self.user_info_uri = "https://www.googleapis.com/oauth2/v3/userinfo"
        self.scope = "openid email profile"

    def get_authorization_url(self, redirect_uri: str) -> str:
        # Print the redirect URI to verify it matches what's in Google Console
        print(f"Creating authorization URL with redirect URI: {redirect_uri}")

        params = {
            "response_type": "code",
            "client_id": self.client_id,  # This MUST be the client ID, not secret
            "redirect_uri": redirect_uri,
            "scope": self.scope,
            "access_type": "offline",  # To get refresh token
            "prompt": "consent",
        }

        # Generate and print the full URL for debugging
        query_string = "&".join(
            [f"{k}={requests.utils.quote(v)}" for k, v in params.items()]
        )
        auth_url = f"{self.auth_uri}?{query_string}"
        print(
            f"Generated auth URL: {auth_url[:100]}..."
        )  # Print just beginning for security

        return auth_url

    def get_user_info(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Get user info from Google using authorization code"""
        # Exchange authorization code for access token
        token_data = self._get_tokens(code, redirect_uri)

        if not token_data or "access_token" not in token_data:
            error_msg = f"Failed to get access token from Google: {token_data.get('error_description', 'Unknown error')}"
            print(error_msg)
            raise ValueError(error_msg)

        # Use the access token to get user info
        access_token = token_data["access_token"]
        print(f"Successfully obtained access token, fetching user info...")

        try:
            # Make sure we're using the token correctly in the Authorization header
            headers = {"Authorization": f"Bearer {access_token}"}

            response = requests.get(self.user_info_uri, headers=headers)

            # Log response for debugging
            print(f"User info response status: {response.status_code}")
            if response.status_code != 200:
                print(f"Error response body: {response.text}")

            response.raise_for_status()
            user_info = response.json()

            print(
                f"Successfully retrieved user info for: {user_info.get('email', 'unknown')}"
            )

            # Add tokens to the user info for later use
            user_info["tokens"] = token_data

            return user_info
        except requests.RequestException as e:
            print(f"Error getting user info: {str(e)}")
            raise ValueError(f"Failed to get user info from Google: {str(e)}")

    def _get_tokens(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens"""
        # Print debug info about the request we're about to make
        print(f"Exchanging code for tokens with redirect_uri: {redirect_uri}")

        # Validate the code format - Google auth codes are typically longer
        if len(code) < 20:
            print(
                f"Warning: Code appears too short ({len(code)} chars), might be invalid"
            )

        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        # Log request details (omitting sensitive info)
        print(f"Token request URL: {self.token_uri}")
        print(
            f"Token request data: client_id={self.client_id[:10]}..., redirect_uri={redirect_uri}"
        )

        try:
            response = requests.post(self.token_uri, data=data)

            # Log the response for debugging
            print(f"Token response status: {response.status_code}")
            if response.status_code != 200:
                print(f"Error response body: {response.text}")
                return {
                    "error": "token_exchange_failed",
                    "error_description": response.text,
                }

            token_data = response.json()
            print(f"Token exchange successful. Access token obtained.")
            return token_data
        except requests.RequestException as e:
            print(f"Request error during token exchange: {str(e)}")
            return {"error": "request_exception", "error_description": str(e)}

    def verify_id_token(self, id_token: str) -> Dict[str, Any]:
        """
        Verify a Google ID token and return the user information if valid.
        This is typically used when the frontend gets the ID token directly
        from Google Sign-In.
        """
        try:
            # For proper verification, use Google's libraries or APIs
            # This is a placeholder for the concept
            from google.oauth2 import id_token as google_id_token
            from google.auth.transport import requests

            # Specify the CLIENT_ID as the audience
            idinfo = google_id_token.verify_oauth2_token(
                id_token, requests.Request(), self.client_id
            )

            # Verify issuer
            if idinfo["iss"] not in [
                "accounts.google.com",
                "https://accounts.google.com",
            ]:
                raise ValueError("Wrong issuer.")

            return idinfo
        except ImportError:
            # If Google libraries not available, try simple JWT decoding
            # For demonstration - in production, always verify signatures properly
            print(
                "Warning: Using simplified ID token verification (not secure for production)"
            )
            return extract_google_info_from_id_token(id_token).raw_data
        except Exception as e:
            print(f"Error verifying ID token: {str(e)}")
            raise ValueError(f"Invalid ID token: {str(e)}")


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


def handle_google_callback(
    db: Session,
    code: str,
    redirect_uri: str = "http://127.0.0.1:8000/api/v1/auth/google/callback",
) -> Tuple[User, bool]:
    """
    Handle Google OAuth callback, creating or retrieving the user.
    Returns (user, is_new_user) tuple.
    """
    try:
        # Check if the code looks like a JWT token (which won't work with Google)
        if code.count(".") == 2 and len(code) < 200:
            print(
                f"Warning: Code appears to be a JWT token which won't work as an auth code"
            )
            return None, False

        # Get user info from Google
        user_info = google_client.get_user_info(code, redirect_uri)

        # Map Google response to our expected format
        oauth_data = {
            "id": user_info.get("sub"),  # Google uses 'sub' for user ID
            "email": user_info.get("email", ""),
            "name": user_info.get("name", ""),
            "picture": user_info.get("picture", ""),
            "tokens": user_info.get("tokens", {}),
        }

        if not oauth_data["id"] or not oauth_data["email"]:
            print(
                f"Error: Missing required OAuth user data. ID: {bool(oauth_data['id'])}, Email: {bool(oauth_data['email'])}"
            )
            return None, False

        # Create or update user from OAuth data
        return create_or_update_user_from_oauth(db, oauth_data, OAuthProvider.GOOGLE)
    except Exception as e:
        print(f"Google callback error: {str(e)}")
        # Return None, False to indicate failure - the calling function will handle this
        return None, False


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
    try:
        # Normalize emails to lowercase
        email = user_info.get("email", "").lower()

        if not email:
            print("Error: OAuth data missing email")
            return None, False

        # Get provider-specific ID
        provider_id = user_info.get("id")
        if not provider_id:
            print("Error: OAuth data missing provider user ID")
            return None, False

        print(f"Processing OAuth login for {email} with provider {provider.value}")

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
            print(f"Found existing OAuth connection for user ID: {user.id}")
            return user, False

        # Check if user exists with this email
        user = db.query(User).filter(User.email == email).first()
        is_new = False

        if not user:
            # Create new user
            print(f"Creating new user for OAuth email: {email}")
            name = user_info.get("name", "")
            picture_url = (
                user_info.get("picture", {}).get("data", {}).get("url")
                if isinstance(user_info.get("picture"), dict)
                else user_info.get("picture")
            )

            import secrets
            import string

            # Generate a secure random password
            random_password = "".join(
                secrets.choice(string.ascii_letters + string.digits) for _ in range(24)
            )

            # Create password hash - we need to import the password hashing function
            from app.core.security import get_password_hash

            # Create user with hashed password
            user = User(
                email=email,
                full_name=name or email.split("@")[0],
                password_hash=get_password_hash(
                    random_password
                ),  # Properly hash the password
                phone="",  # Empty string instead of placeholder
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            is_new = True

        # Create OAuth account link
        print(f"Creating OAuth connection for user ID: {user.id}")
        oauth_connection = OAuthConnection(
            user_id=user.id,
            provider=provider.value,
            provider_user_id=provider_id,
            access_token=user_info.get("tokens", {}).get("access_token", ""),
            refresh_token=user_info.get("tokens", {}).get("refresh_token", ""),
            expires_at=(
                (
                    datetime.now()
                    + timedelta(
                        seconds=user_info.get("tokens", {}).get("expires_in", 3600)
                    )
                ).timestamp()
                if user_info.get("tokens", {}).get("expires_in")
                else None
            ),
        )
        db.add(oauth_connection)
        db.commit()

        return user, is_new
    except Exception as e:
        print(f"Error in create_or_update_user_from_oauth: {str(e)}")
        db.rollback()
        return None, False
