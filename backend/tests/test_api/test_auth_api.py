import pytest
from fastapi import status
from tests.utils import create_random_user_data, create_random_organization_data


def test_login_success(client, test_user):
    """Test successful login."""
    login_data = {"username": test_user.email, "password": "password"}
    response = client.post("/api/v1/auth/login", data=login_data)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    """Test login with wrong password."""
    login_data = {"username": test_user.email, "password": "wrong_password"}
    response = client.post("/api/v1/auth/login", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user(client):
    """Test login with non-existent user."""
    login_data = {"username": "nonexistent@example.com", "password": "password"}
    response = client.post("/api/v1/auth/login", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_register_user(client):
    """Test user registration."""
    user_data = create_random_user_data()
    response = client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["phone"] == user_data["phone"]
    assert data["full_name"] == user_data["full_name"]

    # Test login with the new user
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    login_response = client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == status.HTTP_200_OK


def test_register_with_existing_email(client, test_user):
    """Test registration with an existing email."""
    user_data = create_random_user_data()
    user_data["email"] = test_user.email  # Use existing email

    response = client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_register_with_existing_phone(client, test_user):
    """Test registration with an existing phone."""
    user_data = create_random_user_data()
    user_data["phone"] = test_user.phone  # Use existing phone

    response = client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_register_organization(client):
    """Test registering as an organization owner."""
    user_data = create_random_user_data()
    org_data = create_random_organization_data()

    data = {"user_data": user_data, "organization_data": org_data}

    response = client.post("/api/v1/auth/register-organization", json=data)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["email"] == user_data["email"]

    # Check that the user has admin role
    assert any(role["role"] == "admin" for role in data["roles"])

    # Test login with the new user
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    login_response = client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == status.HTTP_200_OK


def test_register_with_admin_role(client):
    """Test that regular registration cannot include admin role."""
    user_data = create_random_user_data()
    user_data["roles"] = ["admin"]  # Try to register as admin

    response = client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
