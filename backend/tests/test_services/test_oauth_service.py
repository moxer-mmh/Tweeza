import pytest
from unittest.mock import patch, MagicMock
from app.services import oauth_service
from app.schemas import OAuthProvider


@patch("app.services.oauth_service.google_client")
def test_get_google_auth_url(mock_google_client):
    """Test getting Google authentication URL."""
    # Define expected URL
    expected_url = (
        "https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=..."
    )
    mock_google_client.get_authorization_url.return_value = expected_url

    # Call function
    url = oauth_service.get_google_auth_url("http://localhost:3000/callback")

    # Verify
    assert url == expected_url
    mock_google_client.get_authorization_url.assert_called_once()


@patch("app.services.oauth_service.google_client")
def test_google_auth_callback(mock_google_client, db_session):
    """Test handling Google OAuth callback."""
    # Mock user info returned from Google
    mock_google_client.get_user_info.return_value = {
        "email": "test@example.com",
        "name": "Test User",
        "picture": "https://example.com/photo.jpg",
        "sub": "12345",  # Changed from "id" to "sub" to match Google's actual format
    }

    # Call function
    code = "test_auth_code"
    redirect_uri = "http://127.0.0.1:8000/api/v1/auth/google/callback"
    user, is_new = oauth_service.handle_google_callback(db_session, code, redirect_uri)

    # Verify
    assert user is not None
    assert user.email == "test@example.com"
    mock_google_client.get_user_info.assert_called_once_with(code, redirect_uri)


@patch("app.services.oauth_service.facebook_client")
def test_get_facebook_auth_url(mock_fb_client):
    """Test getting Facebook authentication URL."""
    # Mock return value
    expected_url = "https://www.facebook.com/dialog/oauth?client_id=..."
    mock_fb_client.get_authorization_url.return_value = expected_url

    # Call function
    url = oauth_service.get_facebook_auth_url("http://localhost:3000/callback")

    # Verify
    assert url == expected_url
    mock_fb_client.get_authorization_url.assert_called_once()


@patch("app.services.oauth_service.facebook_client")
def test_facebook_auth_callback(mock_fb_client, db_session):
    """Test handling Facebook OAuth callback."""
    # Mock user info returned from Facebook
    mock_fb_client.get_user_info.return_value = {
        "email": "test@example.com",
        "name": "Test User",
        "picture": {"data": {"url": "https://example.com/photo.jpg"}},
        "id": "67890",
    }

    # Call function
    code = "test_auth_code"
    user, is_new = oauth_service.handle_facebook_callback(db_session, code)

    # Verify
    assert user is not None
    assert user.email == "test@example.com"
    mock_fb_client.get_user_info.assert_called_once_with(code)


def test_create_or_update_user_from_oauth(db_session):
    """Test creating or updating a user from OAuth data."""
    oauth_data = {
        "email": "oauth_test@example.com",
        "name": "OAuth User",
        "picture": "https://example.com/photo.jpg",
        "id": "oauth123",
    }
    provider = OAuthProvider.GOOGLE

    # First call should create a new user
    user, is_new = oauth_service.create_or_update_user_from_oauth(
        db_session, oauth_data, provider
    )

    assert is_new is True
    assert user is not None
    assert user.email == oauth_data["email"]
    assert user.full_name == oauth_data["name"]
    # Remove or comment out this line as User model doesn't have profile_image
    # assert user.profile_image == oauth_data["picture"]
