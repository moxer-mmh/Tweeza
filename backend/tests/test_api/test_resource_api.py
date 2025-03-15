import pytest
from fastapi import status
from tests.utils import create_random_resource_request_data


@pytest.fixture
def test_resource_request(db_session, test_event):
    """Create a test resource request."""
    from app.schemas import ResourceTypeEnum
    from app.db.models import ResourceRequest

    # Check if a request already exists
    existing_request = db_session.query(ResourceRequest).first()
    if existing_request:
        return existing_request

    # Create a new request
    request = ResourceRequest(
        event_id=test_event.id,
        resource_type=ResourceTypeEnum.FOOD.value,
        quantity_needed=50,
        quantity_received=0,
    )
    db_session.add(request)
    db_session.commit()
    db_session.refresh(request)

    return request


@pytest.fixture
def test_resource_request_id(test_resource_request):
    """Return ID of test resource request."""
    return test_resource_request.id


def test_create_resource_request(client, admin_token_headers, test_event_id):
    """Test creating a new resource request."""
    request_data = create_random_resource_request_data()

    response = client.post(
        f"/api/v1/resources/requests/event/{test_event_id}",
        json=request_data,
        headers=admin_token_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["resource_type"] == request_data["resource_type"]
    assert data["quantity_needed"] == request_data["quantity_needed"]
    assert data["event_id"] == test_event_id


def test_create_resource_request_unauthorized(client, token_headers, test_event_id):
    """Test that unauthorized users cannot create resource requests."""
    request_data = create_random_resource_request_data()

    response = client.post(
        f"/api/v1/resources/requests/event/{test_event_id}",
        json=request_data,
        headers=token_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_event_resource_requests(client, test_event_id, test_resource_request_id):
    """Test listing resource requests for an event."""
    response = client.get(f"/api/v1/resources/requests/event/{test_event_id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)
    assert any(req["id"] == test_resource_request_id for req in data)


def test_update_resource_request(client, admin_token_headers, test_resource_request_id):
    """Test updating a resource request."""
    new_quantity = 75
    update_data = {"quantity_needed": new_quantity}

    response = client.put(
        f"/api/v1/resources/requests/{test_resource_request_id}",
        json=update_data,
        headers=admin_token_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["quantity_needed"] == new_quantity


def test_update_resource_request_unauthorized(
    client, token_headers, test_resource_request_id
):
    """Test that unauthorized users cannot update resource requests."""
    update_data = {"quantity_needed": 100}

    response = client.put(
        f"/api/v1/resources/requests/{test_resource_request_id}",
        json=update_data,
        headers=token_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_resource_request(client, admin_token_headers, test_event_id):
    """Test deleting a resource request."""
    # Create a new request for testing deletion
    request_data = create_random_resource_request_data()
    create_response = client.post(
        f"/api/v1/resources/requests/event/{test_event_id}",
        json=request_data,
        headers=admin_token_headers,
    )
    created_request_id = create_response.json()["id"]

    # Delete the request
    response = client.delete(
        f"/api/v1/resources/requests/{created_request_id}", headers=admin_token_headers
    )

    assert response.status_code == status.HTTP_200_OK


def test_create_contribution(client, token_headers, test_resource_request_id):
    """Test creating a resource contribution."""
    contribution_data = {"request_id": test_resource_request_id, "quantity": 10}

    response = client.post(
        "/api/v1/resources/contributions", json=contribution_data, headers=token_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["request_id"] == test_resource_request_id
    assert data["quantity"] == 10


def test_get_user_contributions(client, token_headers, test_resource_request_id):
    """Test getting all contributions made by the current user."""
    # First, create a contribution
    contribution_data = {"request_id": test_resource_request_id, "quantity": 15}
    client.post(
        "/api/v1/resources/contributions", json=contribution_data, headers=token_headers
    )

    # Get user contributions
    response = client.get("/api/v1/resources/contributions/user", headers=token_headers)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)
    assert any(
        c["request_id"] == test_resource_request_id and c["quantity"] == 15
        for c in data
    )


def test_get_request_contributions(client, token_headers, test_resource_request_id):
    """Test getting all contributions for a specific request."""
    # First, create a contribution
    contribution_data = {"request_id": test_resource_request_id, "quantity": 20}
    client.post(
        "/api/v1/resources/contributions", json=contribution_data, headers=token_headers
    )

    # Get request contributions
    response = client.get(
        f"/api/v1/resources/contributions/request/{test_resource_request_id}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)
    assert any(
        c["request_id"] == test_resource_request_id and c["quantity"] == 20
        for c in data
    )
