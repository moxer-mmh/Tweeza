import pytest
from datetime import datetime, timedelta
from app.services import analytics_service
from app.db.models import Event, ResourceRequest, ResourceContribution


@pytest.fixture
def test_events_data(db_session, test_organization, test_user):
    """Create test events data for analytics testing."""
    # Create events with different dates
    events = []
    for i in range(3):
        event = Event(
            title=f"Test Event {i}",
            event_type="IFTAR",
            organization_id=test_organization.id,
            start_time=datetime.now() - timedelta(days=i * 10),
            end_time=datetime.now() + timedelta(days=i * 5),
            # Use address instead of location
            address="Test Location",
            status="active",
        )
        db_session.add(event)

    db_session.commit()
    for event in db_session.query(Event).all():
        events.append(event)

    return events


def test_count_entities(db_session, test_events_data, test_user, test_organization):
    """Test counting entities."""
    result = analytics_service.count_entities(db_session)

    assert isinstance(result, dict)
    assert "users" in result
    assert "organizations" in result
    assert "events" in result
    assert "resources" in result

    # Verify counts are positive numbers
    assert result["users"] > 0
    assert result["organizations"] > 0
    assert result["events"] >= len(test_events_data)


def test_resource_contributions_by_type(db_session, test_events_data, test_user):
    """Test resource contributions by type analytics."""
    # Create resource requests with different types
    event = test_events_data[0]

    # Create food request
    food_request = ResourceRequest(
        event_id=event.id,
        resource_type="food",
        quantity_needed=100,
        quantity_received=0,
    )
    db_session.add(food_request)

    # Create money request
    money_request = ResourceRequest(
        event_id=event.id,
        resource_type="money",
        quantity_needed=500,
        quantity_received=0,
    )
    db_session.add(money_request)
    db_session.commit()

    # Create contributions
    for req in [food_request, money_request]:
        contribution = ResourceContribution(
            request_id=req.id,
            user_id=test_user.id,
            quantity=25,
            contribution_time=datetime.now(),
        )
        db_session.add(contribution)

    db_session.commit()

    # Test the function
    result = analytics_service.resource_contributions_by_type(db_session)

    # Verify results
    assert isinstance(result, list)
    assert len(result) >= 2

    # Check that each type is represented
    types = [item["type"] for item in result]
    assert "food" in types
    assert "money" in types


def test_get_event_statistics(db_session, test_events_data):
    """Test getting event statistics."""
    stats = analytics_service.get_event_statistics(db_session)

    # Verify that we get statistics
    assert stats is not None
    assert isinstance(stats, dict)
    assert "total_events" in stats
    assert stats["total_events"] >= len(test_events_data)
    assert "events_by_status" in stats
    assert "events_by_organization" in stats


def test_get_resource_statistics(db_session, test_events_data, test_user):
    """Test getting resource analytics."""
    # Create resource requests for the first event
    event = test_events_data[0]
    resource_request = ResourceRequest(
        event_id=event.id,
        resource_type="food",
        quantity_needed=100,
        quantity_received=0,
    )
    db_session.add(resource_request)
    db_session.commit()

    # Create a contribution
    contribution = ResourceContribution(
        request_id=resource_request.id,
        user_id=test_user.id,
        quantity=50,
        contribution_time=datetime.now(),
    )
    db_session.add(contribution)
    db_session.commit()

    # Update the request to reflect the contribution
    resource_request.quantity_received = 50
    db_session.commit()

    # Get resource analytics
    resource_stats = analytics_service.get_resource_statistics(db_session)

    # Verify
    assert resource_stats is not None
    assert isinstance(resource_stats, dict)
    assert "total_requests" in resource_stats
    assert resource_stats["total_requests"] >= 1
    assert "total_contributions" in resource_stats
    assert resource_stats["total_contributions"] >= 1
    assert "fulfillment_rate" in resource_stats
    assert 0 <= resource_stats["fulfillment_rate"] <= 1
