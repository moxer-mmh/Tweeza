import pytest
from app.services import search_service
from app.db.models import User, Event, Organization, ResourceRequest


@pytest.fixture
def test_search_data(db_session, test_user, test_organization, test_event):
    """Create additional test data for search testing."""
    # Create users with different names
    users = []
    for i, name in enumerate(["John Smith", "Jane Doe", "Alice Johnson"]):
        user = User(
            email=f"search{i}@example.com",
            full_name=name,
            is_active=True,
        )
        db_session.add(user)
        users.append(user)

    # Create organizations with different names
    orgs = []
    for i, name in enumerate(
        ["Charity Foundation", "Helpers Organization", "Community Support"]
    ):
        org = Organization(
            name=name,
            description=f"Description for {name}",
            location=f"Location {i}",
            website=f"https://org{i}.example.com",
        )
        db_session.add(org)
        orgs.append(org)

    # Create events with different titles
    events = []
    for i, title in enumerate(
        ["Food Drive", "Fundraising Event", "Community Workshop"]
    ):
        event = Event(
            title=title,
            description=f"Description for {title}",
            organization_id=test_organization.id,
            start_date="2025-01-01",
            end_date="2025-01-02",
            location=f"Event Location {i}",
            status="active",
        )
        db_session.add(event)
        events.append(event)

    db_session.commit()
    return {"users": users, "organizations": orgs, "events": events}


def test_search_users(db_session, test_search_data):
    """Test searching for users."""
    # Search for "John"
    results = search_service.search_users(db_session, "John")

    assert len(results) >= 1
    assert any(u.full_name == "John Smith" for u in results)

    # Search for "Smith"
    results = search_service.search_users(db_session, "Smith")

    assert len(results) >= 1
    assert any(u.full_name == "John Smith" for u in results)


def test_search_organizations(db_session, test_search_data):
    """Test searching for organizations."""
    # Search for "Charity"
    results = search_service.search_organizations(db_session, "Charity")

    assert len(results) >= 1
    assert any(o.name == "Charity Foundation" for o in results)

    # Search for "Organization"
    results = search_service.search_organizations(db_session, "Organization")

    assert len(results) >= 1
    assert any(o.name == "Helpers Organization" for o in results)


def test_search_events(db_session, test_search_data):
    """Test searching for events."""
    # Search for "Food"
    results = search_service.search_events(db_session, "Food")

    assert len(results) >= 1
    assert any(e.title == "Food Drive" for e in results)

    # Search for "Workshop"
    results = search_service.search_events(db_session, "Workshop")

    assert len(results) >= 1
    assert any(e.title == "Community Workshop" for e in results)


def test_global_search(db_session, test_search_data):
    """Test global search across multiple entity types."""
    # Search for "Community" (should match organization and event)
    results = search_service.global_search(db_session, "Community")

    assert len(results["organizations"]) >= 1
    assert len(results["events"]) >= 1
    assert any(o.name == "Community Support" for o in results["organizations"])
    assert any(e.title == "Community Workshop" for e in results["events"])

    # Search for something that shouldn't exist
    results = search_service.global_search(db_session, "NonExistentTerm")

    assert len(results["users"]) == 0
    assert len(results["organizations"]) == 0
    assert len(results["events"]) == 0


def test_search_with_filters(db_session, test_search_data):
    """Test searching with additional filters."""
    # Search for active events containing "Community"
    results = search_service.search_events(
        db_session, "Community", filters={"status": "active"}
    )

    assert len(results) >= 1
    assert all(e.status == "active" for e in results)
    assert any(e.title == "Community Workshop" for e in results)


def test_search_sorting(db_session, test_search_data):
    """Test search results sorting."""
    # Search for events and sort by title
    results = search_service.search_events(
        db_session,
        "",  # Empty search to get all events
        sort_by="title",
        sort_order="asc",
    )

    # Check if results are sorted
    titles = [e.title for e in results]
    sorted_titles = sorted(titles)
    assert titles == sorted_titles
