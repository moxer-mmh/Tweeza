import pytest
from fastapi import status
from tests.utils import create_random_user_data


def test_read_current_user(client, token_headers, test_user):
    """Test getting current user information."""
    response = client.get("/api/v1/users/me", headers=token_headers)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name


def test_read_current_user_unauthorized(client):
    """Test accessing current user without authentication."""
    response = client.get("/api/v1/users/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_user(client, token_headers, test_user):
    """Test updating user information."""
    new_name = "Updated Test User"
    update_data = {"full_name": new_name}

    response = client.put(
        f"/api/v1/users/{test_user.id}", json=update_data, headers=token_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["full_name"] == new_name


def test_update_other_user_as_regular_user(client, token_headers, test_admin_user):
    """Test that a regular user cannot update another user."""
    update_data = {"full_name": "Should Not Update"}

    response = client.put(
        f"/api/v1/users/{test_admin_user.id}", json=update_data, headers=token_headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_user_as_admin(
    client, admin_token_headers, test_user, test_organization
):
    """Test that an admin can update another user."""
    new_name = "Admin Updated User"
    update_data = {"full_name": new_name}

    response = client.put(
        f"/api/v1/users/{test_user.id}", json=update_data, headers=admin_token_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["full_name"] == new_name


def test_update_user_as_super_admin(client, super_admin_token_headers, test_user):
    """Test that a super admin can update any user."""
    new_name = "Super Admin Updated User"
    update_data = {"full_name": new_name}

    response = client.put(
        f"/api/v1/users/{test_user.id}",
        json=update_data,
        headers=super_admin_token_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["full_name"] == new_name


def test_get_user(client, token_headers, test_user):
    """Test getting user by ID."""
    response = client.get(f"/api/v1/users/{test_user.id}", headers=token_headers)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email


def test_list_users_as_regular_user(client, token_headers):
    """Test that regular users cannot list all users."""
    response = client.get("/api/v1/users/", headers=token_headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_users_as_admin(client, admin_token_headers):
    """Test that admins can list users in their organization."""
    response = client.get("/api/v1/users/", headers=admin_token_headers)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)


def test_list_users_as_super_admin(client, super_admin_token_headers):
    """Test that super admins can list all users."""
    response = client.get("/api/v1/users/", headers=super_admin_token_headers)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)
    # Check that we get at least one user (the super_admin themselves)
    assert len(data) >= 1

    # Check that the super admin is in the response
    assert any(user["email"] == "superadmin@example.com" for user in data)


def test_add_role_to_user(client, token_headers, test_user):
    """Test adding a role to own user profile."""
    role_data = {"role": "volunteer"}

    response = client.post(
        f"/api/v1/users/{test_user.id}/roles", json=role_data, headers=token_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert any(role["role"] == "volunteer" for role in data["roles"])


def test_add_admin_role_as_regular_user(client, token_headers, test_user):
    """Test that regular users cannot add admin roles."""
    role_data = {"role": "admin"}

    response = client.post(
        f"/api/v1/users/{test_user.id}/roles", json=role_data, headers=token_headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_remove_role_from_user(client, token_headers, test_user):
    """Test removing a role from a user."""
    # First add a role
    role_data = {"role": "volunteer"}
    client.post(
        f"/api/v1/users/{test_user.id}/roles", json=role_data, headers=token_headers
    )

    # Then remove it
    response = client.delete(
        f"/api/v1/users/{test_user.id}/roles/volunteer", headers=token_headers
    )

    assert response.status_code == status.HTTP_200_OK
