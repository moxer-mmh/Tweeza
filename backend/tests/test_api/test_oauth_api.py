import pytest
from unittest.mock import patch
from fastapi import status
from app.services import oauth_service


@patch("app.api.v1.endpoints.auth.oauth_service.get_google_auth_url")
def test_google_auth_url(mock_get_url, client):
    """Test getting a Google OAuth URL."""
    # Mock return value
    mock_get_url.return_value = (
        "https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=..."
    )

    # Make request
    response = client.get("/api/v1/auth/google/login")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "url" in data
    assert data["url"] == mock_get_url.return_value


@patch("app.api.v1.endpoints.auth.oauth_service.handle_google_callback")
def test_google_callback(mock_handle_callback, client, test_user):
    """Test handling Google OAuth callback."""
    # Mock return value
    mock_handle_callback.return_value = (test_user, True)

    # Make request
    response = client.get("/api/v1/auth/google/callback?code=test_auth_code")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


@patch("app.api.v1.endpoints.auth.oauth_service.get_facebook_auth_url")
def test_facebook_auth_url(mock_get_url, client):
    """Test getting a Facebook OAuth URL."""
    # Mock return value
    mock_get_url.return_value = "https://www.facebook.com/dialog/oauth?client_id=..."

    # Make request
    response = client.get("/api/v1/auth/facebook/login")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "url" in data
    assert data["url"] == mock_get_url.return_value


@patch("app.api.v1.endpoints.auth.oauth_service.handle_facebook_callback")
def test_facebook_callback(mock_handle_callback, client, test_user):
    """Test handling Facebook OAuth callback."""
    # Mock return value
    mock_handle_callback.return_value = (test_user, True)

    # Make request
    response = client.get("/api/v1/auth/facebook/callback?code=test_auth_code")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
