import pytest
from datetime import datetime, timedelta
from app.services import event_service
from app.schemas import (
    EventCreate,
    EventUpdate,
    EventCollaboratorCreate,
    EventBeneficiaryCreate,
    EventTypeEnum,
)
from app.db.models import Event
from tests.utils import create_random_event_data


@pytest.fixture
def test_event(db_session, test_organization):
    """Create a test event."""
    event_data = {
        "title": "Test Event",
        "event_type": EventTypeEnum.IFTAR.value,
        "start_time": datetime.now() + timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=1, hours=2),
        "organization_id": test_organization.id,
    }

    event = Event(**event_data)
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    return event


def test_create_event(db_session, test_organization):
    """Test event creation."""
    event_data = create_random_event_data(test_organization.id)
    event_schema = EventCreate(**event_data)

    event = event_service.create_event(db_session, event_schema)

    assert event.title == event_data["title"]
    assert event.organization_id == test_organization.id


def test_get_event(db_session, test_event):
    """Test getting event by ID."""
    event = event_service.get_event(db_session, test_event.id)
    assert event is not None
    assert event.id == test_event.id
    assert event.title == test_event.title


def test_get_events(db_session, test_event):
    """Test getting list of events."""
    events = event_service.get_events(db_session)
    assert len(events) >= 1
    assert any(e.id == test_event.id for e in events)


def test_get_events_by_organization(db_session, test_event, test_organization):
    """Test getting events for an organization."""
    events = event_service.get_events_by_organization(db_session, test_organization.id)
    assert len(events) >= 1
    assert any(e.id == test_event.id for e in events)


def test_get_upcoming_events(db_session, test_event):
    """Test getting upcoming events."""
    # Our test event is already in the future
    upcoming_events = event_service.get_upcoming_events(db_session)
    assert len(upcoming_events) >= 1
    assert any(e.id == test_event.id for e in upcoming_events)


def test_update_event(db_session, test_event):
    """Test updating event."""
    new_title = "Updated Event Title"
    update_data = EventUpdate(title=new_title)

    updated_event = event_service.update_event(db_session, test_event.id, update_data)

    assert updated_event is not None
    assert updated_event.title == new_title


def test_delete_event(db_session, test_organization):
    """Test event deletion."""
    # Create an event to delete
    event_data = create_random_event_data(test_organization.id)
    event_schema = EventCreate(**event_data)
    event = event_service.create_event(db_session, event_schema)

    # Delete the event
    success = event_service.delete_event(db_session, event.id)
    assert success is True

    # Verify event is gone
    deleted_event = event_service.get_event(db_session, event.id)
    assert deleted_event is None


def test_add_collaborator_to_event(db_session, test_event, test_organization):
    """Test adding a collaborating organization to an event."""
    # Create a second organization to be the collaborator
    from app.db.models import Organization

    collab_org = Organization(
        name="Collaborator Organization",
        description="A collaborator",
        location="Collab Location",
    )
    db_session.add(collab_org)
    db_session.commit()
    db_session.refresh(collab_org)

    collaborator_data = EventCollaboratorCreate(organization_id=collab_org.id)

    collaborator = event_service.add_collaborator_to_event(
        db_session, test_event.id, collaborator_data
    )

    assert collaborator is not None
    assert collaborator.organization_id == collab_org.id
    assert collaborator.event_id == test_event.id


def test_get_event_collaborators(db_session, test_event, test_organization):
    """Test getting collaborating organizations for an event."""
    # Create a collaborator organization
    from app.db.models import Organization

    collab_org = Organization(
        name="Collaborator Organization 2",
        description="Another collaborator",
        location="Collab Location 2",
    )
    db_session.add(collab_org)
    db_session.commit()
    db_session.refresh(collab_org)

    # Add as collaborator
    collaborator_data = EventCollaboratorCreate(organization_id=collab_org.id)
    event_service.add_collaborator_to_event(
        db_session, test_event.id, collaborator_data
    )

    # Get collaborators
    collaborators = event_service.get_event_collaborators(db_session, test_event.id)

    assert len(collaborators) >= 1
    assert any(c.id == collab_org.id for c in collaborators)


def test_add_beneficiary_to_event(db_session, test_event, test_user):
    """Test adding a beneficiary to an event."""
    beneficiary_data = EventBeneficiaryCreate(user_id=test_user.id)

    beneficiary = event_service.add_beneficiary_to_event(
        db_session, test_event.id, beneficiary_data
    )

    assert beneficiary is not None
    assert beneficiary.user_id == test_user.id
    assert beneficiary.event_id == test_event.id


def test_get_event_beneficiaries(db_session, test_event, test_user):
    """Test getting beneficiaries for an event."""
    # Add a beneficiary
    beneficiary_data = EventBeneficiaryCreate(user_id=test_user.id)
    event_service.add_beneficiary_to_event(db_session, test_event.id, beneficiary_data)

    # Get beneficiaries
    beneficiaries = event_service.get_event_beneficiaries(db_session, test_event.id)

    assert len(beneficiaries) >= 1
    assert any(b.id == test_user.id for b in beneficiaries)


def test_remove_collaborator_from_event(db_session, test_event):
    """Test removing a collaborator from an event."""
    # Create and add a collaborator
    from app.db.models import Organization

    collab_org = Organization(
        name="Temporary Collaborator",
        description="To be removed",
        location="Temp Location",
    )
    db_session.add(collab_org)
    db_session.commit()
    db_session.refresh(collab_org)

    collaborator_data = EventCollaboratorCreate(organization_id=collab_org.id)
    event_service.add_collaborator_to_event(
        db_session, test_event.id, collaborator_data
    )

    # Remove the collaborator
    success = event_service.remove_collaborator_from_event(
        db_session, test_event.id, collab_org.id
    )

    assert success is True

    # Verify collaborator is removed
    collaborators = event_service.get_event_collaborators(db_session, test_event.id)
    assert not any(c.id == collab_org.id for c in collaborators)


def test_get_nearby_events(db_session, test_organization):
    """Test finding events near a location."""
    # Create test events with coordinates
    from app.schemas import EventCreate
    from app.services import event_service

    event_data1 = {
        "title": "Event Near",
        "event_type": "IFTAR",
        "start_time": datetime.now() + timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=1, hours=2),
        "organization_id": test_organization.id,  # Use test_organization instead of hardcoded ID
        "latitude": 36.7528,
        "longitude": 3.0429,  # Algiers coordinates
        "address": "Algiers Center",
    }

    event_data2 = {
        "title": "Event Far",
        "event_type": "IFTAR",
        "start_time": datetime.now() + timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=1, hours=2),
        "organization_id": test_organization.id,  # Use test_organization instead of hardcoded ID
        "latitude": 35.2,
        "longitude": 0.6377,  # Far from Algiers
        "address": "Distant Location",
    }

    event1 = event_service.create_event(db_session, EventCreate(**event_data1))
    event2 = event_service.create_event(db_session, EventCreate(**event_data2))

    # Test nearby search (near Algiers)
    nearby_events = event_service.get_nearby_events(
        db_session, latitude=36.75, longitude=3.04, radius=10  # 10km radius
    )

    assert len(nearby_events) == 1
    assert nearby_events[0].id == event1.id
    assert hasattr(nearby_events[0], "distance")
    assert nearby_events[0].distance < 10  # Should be less than 10km


def test_search_events_by_address(db_session, test_organization):
    """Test searching events by address."""
    from app.schemas import EventCreate
    from app.services import event_service

    # Create test events with addresses
    event_data1 = {
        "title": "Event Algiers",
        "event_type": "IFTAR",
        "start_time": datetime.now() + timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=1, hours=2),
        "organization_id": test_organization.id,
        "address": "Algiers Center, Algeria",
    }

    event_data2 = {
        "title": "Event Oran",
        "event_type": "IFTAR",
        "start_time": datetime.now() + timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=1, hours=2),
        "organization_id": test_organization.id,
        "address": "Oran City, Algeria",
    }

    event1 = event_service.create_event(db_session, EventCreate(**event_data1))
    event2 = event_service.create_event(db_session, EventCreate(**event_data2))

    # Test address search
    algiers_events = event_service.search_events_by_address(db_session, "Algiers")
    assert len(algiers_events) == 1
    assert algiers_events[0].id == event1.id

    # Test address search with event type filter
    all_events = event_service.search_events_by_address(
        db_session, "Algeria", event_type="IFTAR"
    )
    assert len(all_events) == 2
