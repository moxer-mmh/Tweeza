import pytest
from fastapi import status
from tests.utils import create_random_organization_data


def test_create_organization(client, token_headers):
    """Test creating a new organization."""
    org_data = create_random_organization_data()

    response = client.post(
        "/api/v1/organizations/", json=org_data, headers=token_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == org_data["name"]
    assert data["description"] == org_data["description"]


def test_list_organizations(client):
    """Test listing organizations - should be publicly accessible."""
    response = client.get("/api/v1/organizations/")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)


def test_get_my_organizations(client, token_headers, test_organization):
    """Test getting organizations where the current user is a member."""
    response = client.get(
        "/api/v1/organizations/my-organizations", headers=token_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)


def test_get_organization(client, test_organization):
    """Test getting organization by ID - should be publicly accessible."""
    response = client.get(f"/api/v1/organizations/{test_organization.id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == test_organization.id
    assert data["name"] == test_organization.name


def test_update_organization_as_admin(client, admin_token_headers, test_organization):
    """Test updating an organization as an admin."""
    new_name = "Updated Organization"
    update_data = {"name": new_name}

    response = client.put(
        f"/api/v1/organizations/{test_organization.id}",
        json=update_data,
        headers=admin_token_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == new_name


def test_update_organization_as_unauthorized_user(
    client, token_headers, test_organization
):
    """Test that unauthorized users cannot update an organization."""
    update_data = {"name": "Should Not Update"}

    response = client.put(
        f"/api/v1/organizations/{test_organization.id}",
        json=update_data,
        headers=token_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_organization_as_admin(client, admin_token_headers):
    """Test deleting an organization as an admin."""
    # Create a new organization for testing deletion
    org_data = create_random_organization_data()
    create_response = client.post(
        "/api/v1/organizations/", json=org_data, headers=admin_token_headers
    )
    created_org_id = create_response.json()["id"]

    # Delete the organization
    response = client.delete(
        f"/api/v1/organizations/{created_org_id}", headers=admin_token_headers
    )

    assert response.status_code == status.HTTP_200_OK

    # Verify it's deleted
    get_response = client.get(f"/api/v1/organizations/{created_org_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_organization_as_unauthorized_user(
    client, token_headers, test_organization
):
    """Test that unauthorized users cannot delete an organization."""
    response = client.delete(
        f"/api/v1/organizations/{test_organization.id}", headers=token_headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_add_member_to_organization(
    client, admin_token_headers, test_organization, test_user
):
    """Test adding a member to an organization."""
    member_data = {"user_id": test_user.id, "role": "worker"}

    response = client.post(
        f"/api/v1/organizations/{test_organization.id}/members",
        json=member_data,
        headers=admin_token_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["user_id"] == test_user.id
    assert data["organization_id"] == test_organization.id
    assert data["role"] == "worker"


def test_add_member_to_organization_unauthorized(
    client, token_headers, test_organization, test_admin_user
):
    """Test that unauthorized users cannot add members to an organization."""
    member_data = {"user_id": test_admin_user.id, "role": "worker"}

    response = client.post(
        f"/api/v1/organizations/{test_organization.id}/members",
        json=member_data,
        headers=token_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_organization_members(client, test_organization):
    """Test listing organization members - should be publicly accessible."""
    response = client.get(f"/api/v1/organizations/{test_organization.id}/members")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # At least the admin user


def test_remove_member_from_organization(
    client, admin_token_headers, test_organization, test_user
):
    """Test removing a member from an organization."""
    # First, add the user as a member
    member_data = {"user_id": test_user.id, "role": "worker"}
    client.post(
        f"/api/v1/organizations/{test_organization.id}/members",
        json=member_data,
        headers=admin_token_headers,
    )

    # Then remove them
    response = client.delete(
        f"/api/v1/organizations/{test_organization.id}/members/{test_user.id}",
        headers=admin_token_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    # Verify they're removed
    members_response = client.get(
        f"/api/v1/organizations/{test_organization.id}/members"
    )
    members = members_response.json()
    assert not any(m["user_id"] == test_user.id for m in members)


def test_user_can_remove_self_from_organization(
    client, token_headers, test_organization, test_user
):
    """Test that a user can remove themselves from an organization."""
    # First, add the user as a member
    member_data = {"user_id": test_user.id, "role": "worker"}
    # Need admin token to add member
    login_data = {"username": "admin@example.com", "password": "adminpass"}
    response = client.post("/api/v1/auth/login", data=login_data)
    admin_token = response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    client.post(
        f"/api/v1/organizations/{test_organization.id}/members",
        json=member_data,
        headers=admin_headers,
    )

    # Now user can remove themselves
    response = client.delete(
        f"/api/v1/organizations/{test_organization.id}/members/{test_user.id}",
        headers=token_headers,
    )

    assert response.status_code == status.HTTP_200_OK
