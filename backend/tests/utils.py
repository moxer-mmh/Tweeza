from datetime import datetime, timedelta
from app.schemas import UserRoleEnum, EventTypeEnum, ResourceTypeEnum


def create_random_user_data():
    """Generate random user data for testing."""
    import random
    import string

    random_string = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))

    return {
        "email": f"user_{random_string}@example.com",
        "phone": f"123{random_string[:8]}",
        "password": "testpass123",
        "full_name": f"Test User {random_string}",
        "location": "Test Location",
        "latitude": 0.0,
        "longitude": 0.0,
        "roles": [],
    }


def create_random_organization_data():
    """Generate random organization data for testing."""
    import random
    import string

    random_string = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))

    return {
        "name": f"Organization {random_string}",
        "description": f"Description for organization {random_string}",
        "location": "Test Location",
        "latitude": 0.0,
        "longitude": 0.0,
    }


def create_random_event_data(organization_id):
    """Generate random event data for testing."""
    import random
    import string

    random_string = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)

    return {
        "title": f"Event {random_string}",
        "event_type": random.choice([e.value for e in EventTypeEnum]),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "organization_id": organization_id,
    }


def create_random_resource_request_data(event_id=None):
    """Generate random resource request data for testing."""
    import random

    resource_types = [r.value for r in ResourceTypeEnum]

    return {
        "event_id": event_id,
        "resource_type": random.choice(resource_types),
        "quantity_needed": random.randint(5, 100),
        "quantity_received": 0,
    }
