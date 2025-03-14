import pytest
from app.services import resource_service
from app.schemas import (
    ResourceRequestCreate,
    ResourceRequestUpdate,
    ResourceContributionCreate,
    ResourceTypeEnum,
)
from app.db.models import ResourceRequest, ResourceContribution
from tests.utils import create_random_resource_request_data


@pytest.fixture
def test_resource_request(db_session, test_event):
    """Create a test resource request."""
    request_data = {
        "event_id": test_event.id,
        "resource_type": ResourceTypeEnum.FOOD.value,
        "quantity_needed": 50,
        "quantity_received": 0,
    }

    request = ResourceRequest(**request_data)
    db_session.add(request)
    db_session.commit()
    db_session.refresh(request)

    return request


def test_get_resource_request(db_session, test_resource_request):
    """Test getting a resource request by ID."""
    request = resource_service.get_resource_request(
        db_session, test_resource_request.id
    )

    assert request is not None
    assert request.id == test_resource_request.id
    assert request.resource_type == test_resource_request.resource_type


def test_get_resource_requests_by_event(db_session, test_event, test_resource_request):
    """Test getting resource requests for a specific event."""
    requests = resource_service.get_resource_requests_by_event(
        db_session, test_event.id
    )

    assert len(requests) >= 1
    assert any(r.id == test_resource_request.id for r in requests)


def test_create_resource_request(db_session, test_event):
    """Test creating a new resource request."""
    request_data = create_random_resource_request_data()
    request_schema = ResourceRequestCreate(**request_data)

    request = resource_service.create_resource_request(
        db_session, test_event.id, request_schema
    )

    assert request is not None
    assert request.resource_type == request_data["resource_type"]
    assert request.quantity_needed == request_data["quantity_needed"]
    assert request.event_id == test_event.id
    assert request.quantity_received == 0


def test_update_resource_request(db_session, test_resource_request):
    """Test updating a resource request."""
    new_quantity = 75
    update_data = ResourceRequestUpdate(quantity_needed=new_quantity)

    updated_request = resource_service.update_resource_request(
        db_session, test_resource_request.id, update_data
    )

    assert updated_request is not None
    assert updated_request.quantity_needed == new_quantity


def test_delete_resource_request(db_session, test_event):
    """Test deleting a resource request."""
    # Create a request to delete
    request_data = create_random_resource_request_data()
    request_schema = ResourceRequestCreate(**request_data)
    request = resource_service.create_resource_request(
        db_session, test_event.id, request_schema
    )

    # Delete the request
    success = resource_service.delete_resource_request(db_session, request.id)

    assert success is True

    # Verify it's deleted
    deleted_request = resource_service.get_resource_request(db_session, request.id)
    assert deleted_request is None


def test_create_resource_contribution(db_session, test_resource_request, test_user):
    """Test creating a resource contribution."""
    contribution_data = ResourceContributionCreate(
        request_id=test_resource_request.id, quantity=10
    )

    contribution = resource_service.create_resource_contribution(
        db_session, test_user.id, contribution_data
    )

    assert contribution is not None
    assert contribution.request_id == test_resource_request.id
    assert contribution.user_id == test_user.id
    assert contribution.quantity == 10

    # Check that quantity received is updated
    updated_request = resource_service.get_resource_request(
        db_session, test_resource_request.id
    )
    assert updated_request.quantity_received == 10


def test_get_contributions_by_user(db_session, test_resource_request, test_user):
    """Test getting all contributions made by a user."""
    # Create a contribution
    contribution_data = ResourceContributionCreate(
        request_id=test_resource_request.id, quantity=15
    )
    resource_service.create_resource_contribution(
        db_session, test_user.id, contribution_data
    )

    # Get user contributions
    contributions = resource_service.get_contributions_by_user(db_session, test_user.id)

    assert len(contributions) >= 1
    assert any(c.user_id == test_user.id and c.quantity == 15 for c in contributions)


def test_get_contributions_by_request(db_session, test_resource_request, test_user):
    """Test getting all contributions for a specific request."""
    # Create a contribution
    contribution_data = ResourceContributionCreate(
        request_id=test_resource_request.id, quantity=20
    )
    resource_service.create_resource_contribution(
        db_session, test_user.id, contribution_data
    )

    # Get request contributions
    contributions = resource_service.get_contributions_by_request(
        db_session, test_resource_request.id
    )

    assert len(contributions) >= 1
    assert any(
        c.request_id == test_resource_request.id and c.quantity == 20
        for c in contributions
    )


def test_multiple_contributions_update_quantity(
    db_session, test_resource_request, test_user
):
    """Test that multiple contributions update the quantity received correctly."""
    # First contribution
    contribution_data1 = ResourceContributionCreate(
        request_id=test_resource_request.id, quantity=5
    )
    resource_service.create_resource_contribution(
        db_session, test_user.id, contribution_data1
    )

    # Second contribution
    contribution_data2 = ResourceContributionCreate(
        request_id=test_resource_request.id, quantity=7
    )
    resource_service.create_resource_contribution(
        db_session, test_user.id, contribution_data2
    )

    # Check that quantity received is updated correctly
    updated_request = resource_service.get_resource_request(
        db_session, test_resource_request.id
    )
    assert updated_request.quantity_received == 12  # 5 + 7
