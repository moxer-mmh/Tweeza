import os
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.security import get_password_hash, create_access_token
from app.schemas import UserRoleEnum
from app.db.models import User, UserRole, Organization, OrganizationMember


@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database engine with proper SQLite settings."""
    # Use in-memory SQLite for testing with foreign key support
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )

    # Enable foreign keys in SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Clean up after tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db_engine):
    """Create a fresh database session for a test with proper cleanup."""
    connection = test_db_engine.connect()
    transaction = connection.begin()

    Session = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = Session()

    yield session

    # Clean up after test
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """Create a test client with overridden dependencies."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    # Check if user already exists
    existing_user = (
        db_session.query(User).filter(User.email == "user@example.com").first()
    )
    if existing_user:
        return existing_user

    user = User(
        email="user@example.com",
        phone="123456789",
        password_hash=get_password_hash("password"),
        full_name="Test User",
        location="Test Location",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture
def test_admin_user(db_session):
    """Create a test admin user with admin role."""
    # Check if user already exists
    existing_user = (
        db_session.query(User).filter(User.email == "admin@example.com").first()
    )
    if existing_user:
        return existing_user

    user = User(
        email="admin@example.com",
        phone="987654321",
        password_hash=get_password_hash("adminpass"),
        full_name="Admin User",
        location="Admin Location",
    )
    db_session.add(user)
    db_session.commit()

    # Add admin role
    role = UserRole(user_id=user.id, role=UserRoleEnum.ADMIN.value)
    db_session.add(role)
    db_session.commit()

    db_session.refresh(user)
    return user


@pytest.fixture
def test_super_admin(db_session):
    """Create a test super admin user."""
    # Check if user already exists
    existing_user = (
        db_session.query(User).filter(User.email == "superadmin@example.com").first()
    )
    if existing_user:
        return existing_user

    user = User(
        email="superadmin@example.com",
        phone="555555555",
        password_hash=get_password_hash("superpass"),
        full_name="Super Admin",
        location="Super Location",
    )
    db_session.add(user)
    db_session.commit()

    # Add super admin role
    role = UserRole(user_id=user.id, role=UserRoleEnum.SUPER_ADMIN.value)
    db_session.add(role)
    db_session.commit()

    db_session.refresh(user)
    return user


@pytest.fixture
def test_organization(db_session, test_admin_user, test_user):
    """Create a test organization."""
    # Check if organization already exists
    existing_org = (
        db_session.query(Organization)
        .filter(Organization.name == "Test Organization")
        .first()
    )
    if existing_org:
        # Make sure test_user is a member
        existing_user_member = (
            db_session.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id == existing_org.id,
                OrganizationMember.user_id == test_user.id,
            )
            .first()
        )

        if not existing_user_member:
            # Add test_user as a member
            member = OrganizationMember(
                organization_id=existing_org.id,
                user_id=test_user.id,
                role=UserRoleEnum.WORKER.value,
            )
            db_session.add(member)
            db_session.commit()

        return existing_org

    org = Organization(
        name="Test Organization",
        description="Test Description",
        location="Test Location",
        latitude=0.0,
        longitude=0.0,
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)

    # Check if member relation already exists
    existing_member = (
        db_session.query(OrganizationMember)
        .filter(
            OrganizationMember.organization_id == org.id,
            OrganizationMember.user_id == test_admin_user.id,
        )
        .first()
    )

    if not existing_member:
        # Add admin as member with admin role
        member = OrganizationMember(
            organization_id=org.id,
            user_id=test_admin_user.id,
            role=UserRoleEnum.ADMIN.value,
        )
        db_session.add(member)

    # Add test_user as a regular member
    user_member = OrganizationMember(
        organization_id=org.id,
        user_id=test_user.id,
        role=UserRoleEnum.WORKER.value,
    )
    db_session.add(user_member)
    db_session.commit()

    return org


@pytest.fixture
def token_headers(test_user):
    """Get token headers for authenticated requests, bypassing login."""
    # Generate token directly rather than using the login endpoint
    token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_token_headers(test_admin_user):
    """Get token headers for authenticated admin requests, bypassing login."""
    # Generate token directly rather than using the login endpoint
    token = create_access_token(subject=test_admin_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def super_admin_token_headers(test_super_admin):
    """Get token headers for authenticated super admin requests, bypassing login."""
    # Generate token directly rather than using the login endpoint
    token = create_access_token(subject=test_super_admin.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_event(db_session, test_organization):
    """Create a test event for testing."""
    from app.db.models import Event
    from datetime import datetime, timedelta

    # Check if an event already exists
    existing_event = db_session.query(Event).first()
    if existing_event:
        return existing_event

    # Create a new event
    from app.schemas import EventTypeEnum

    event = Event(
        title="Test Event",
        event_type=EventTypeEnum.IFTAR.value,
        start_time=datetime.now() + timedelta(days=1),
        end_time=datetime.now() + timedelta(days=1, hours=2),
        organization_id=test_organization.id,
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    return event


@pytest.fixture
def test_event_id(test_event):
    """Return ID of test event."""
    return test_event.id
