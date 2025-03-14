import pytest
from fastapi import status
from tests.utils import create_random_event_data
from app.schemas import EventTypeEnum
from datetime import datetime, timedelta


@pytest.fixture
def test_event_id(test_event):
    """Get ID of the test event."""
    return test_event.id


def test_create_event(client, admin_token_headers, test_organization):
    """Test creating a new event."""
    event_data = create_random_event_data(test_organization.id)

    response = client.post(
        "/api/v1/events/", json=event_data, headers=admin_token_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["title"] == event_data["title"]
    assert data["organization_id"] == test_organization.id


def test_create_event_unauthorized(client, token_headers, test_organization):
    """Test that unauthorized users cannot create events."""
    event_data = create_random_event_data(test_organization.id)

    response = client.post("/api/v1/events/", json=event_data, headers=token_headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_events(client):
    """Test listing events - should be publicly accessible."""
    response = client.get("/api/v1/events/")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)


def test_get_upcoming_events(client):
    """Test getting upcoming events."""
    response = client.get("/api/v1/events/upcoming")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)


def test_get_organization_events(client, test_organization, test_event_id):
    """Test getting events for a specific organization."""
    response = client.get(f"/api/v1/events/organization/{test_organization.id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)
    assert any(event["id"] == test_event_id for event in data)


def test_get_event(client, test_event_id):
    """Test getting event by ID."""
    response = client.get(f"/api/v1/events/{test_event_id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == test_event_id


def test_update_event(client, admin_token_headers, test_event_id):
    """Test updating an event."""
    new_title = "Updated Event Title"
    update_data = {"title": new_title}

    response = client.put(
        f"/api/v1/events/{test_event_id}", json=update_data, headers=admin_token_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["title"] == new_title


def test_update_event_unauthorized(client, token_headers, test_event_id):
    """Test that unauthorized users cannot update events."""
    update_data = {"title": "Should Not Update"}

    response = client.put(
        f"/api/v1/events/{test_event_id}", json=update_data, headers=token_headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_event(client, admin_token_headers, test_organization):
    """Test deleting an event."""
    # Create a new event for testing deletion
    event_data = create_random_event_data(test_organization.id)
    create_response = client.post(
        "/api/v1/events/", json=event_data, headers=admin_token_headers
    )
    created_event_id = create_response.json()["id"]

    # Delete the event
    response = client.delete(
        f"/api/v1/events/{created_event_id}", headers=admin_token_headers
    )

    assert response.status_code == status.HTTP_200_OK

    # Verify it's deleted
    get_response = client.get(f"/api/v1/events/{created_event_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_add_collaborator_to_event(client, admin_token_headers, test_event_id):
    """Test adding a collaborating organization to an event."""
    # First, create a new organization to be the collaborator
    from tests.utils import create_random_organization_data

    org_data = create_random_organization_data()
    org_response = client.post(
        "/api/v1/organizations/", json=org_data, headers=admin_token_headers
    )
    org_id = org_response.json()["id"]

    # Add as collaborator
    collaborator_data = {"organization_id": org_id}
    response = client.post(
        f"/api/v1/events/{test_event_id}/collaborators",
        json=collaborator_data,
        headers=admin_token_headers,
    )

    assert response.status_code == status.HTTP_200_OK


def test_remove_collaborator_from_event(client, admin_token_headers, test_event_id):
    """Test removing a collaborating organization from an event."""
    # First, create a new organization and add as collaborator
    from tests.utils import create_random_organization_data

    org_data = create_random_organization_data()
    org_response = client.post(
        "/api/v1/organizations/", json=org_data, headers=admin_token_headers
    )
    org_id = org_response.json()["id"]

    # Add as collaborator
    collaborator_data = {"organization_id": org_id}
    client.post(
        f"/api/v1/events/{test_event_id}/collaborators",
        json=collaborator_data,
        headers=admin_token_headers,
    )

    # Remove collaborator
    response = client.delete(
        f"/api/v1/events/{test_event_id}/collaborators/{org_id}",
        headers=admin_token_headers,
    )

    assert response.status_code == status.HTTP_200_OK


def test_add_beneficiary_to_event(
    client, admin_token_headers, test_event_id, test_user
):
    """Test adding a beneficiary to an event."""
    beneficiary_data = {"user_id": test_user.id}
    response = client.post(
        f"/api/v1/events/{test_event_id}/beneficiaries",
        json=beneficiary_data,
        headers=admin_token_headers,
    )

    assert response.status_code == status.HTTP_200_OK


def test_list_event_beneficiaries(
    client, admin_token_headers, test_event_id, test_user
):
    """Test listing beneficiaries for an event."""
    # First, add a beneficiary
    beneficiary_data = {"user_id": test_user.id}
    client.post(
        f"/api/v1/events/{test_event_id}/beneficiaries",
        json=beneficiary_data,
        headers=admin_token_headers,
    )

    # List beneficiaries
    response = client.get(f"/api/v1/events/{test_event_id}/beneficiaries")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)
    assert any(b["id"] == test_user.id for b in data)
