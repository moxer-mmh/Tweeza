import pytest
from app.services import user_service
from app.schemas import UserCreate, UserUpdate, UserRoleEnum
from app.db.models import User, UserRole
from tests.utils import create_random_user_data


def test_create_user(db_session):
    """Test user creation."""
    user_data = create_random_user_data()
    user_schema = UserCreate(**user_data)

    user = user_service.create_user(db_session, user_schema)

    assert user.email == user_data["email"]
    assert user.phone == user_data["phone"]
    assert user.full_name == user_data["full_name"]


def test_get_user_by_email(db_session, test_user):
    """Test getting user by email."""
    user = user_service.get_user_by_email(db_session, test_user.email)
    assert user is not None
    assert user.id == test_user.id


def test_get_user_by_phone(db_session, test_user):
    """Test getting user by phone."""
    user = user_service.get_user_by_phone(db_session, test_user.phone)
    assert user is not None
    assert user.id == test_user.id


def test_get_user_by_id(db_session, test_user):
    """Test getting user by ID."""
    user = user_service.get_user(db_session, test_user.id)
    assert user is not None
    assert user.email == test_user.email


def test_get_users(db_session, test_user):
    """Test getting list of users."""
    users = user_service.get_users(db_session)
    assert len(users) >= 1
    assert any(u.id == test_user.id for u in users)


def test_update_user(db_session, test_user):
    """Test updating user."""
    new_name = "Updated Name"
    update_data = UserUpdate(full_name=new_name)

    updated_user = user_service.update_user(db_session, test_user.id, update_data)

    assert updated_user is not None
    assert updated_user.full_name == new_name


def test_add_role_to_user(db_session, test_user):
    """Test adding role to user."""
    role = UserRoleEnum.VOLUNTEER

    user_role = user_service.add_role_to_user(db_session, test_user.id, role)

    assert user_role is not None
    assert user_role.role == role.value

    # Check the user object
    user = user_service.get_user(db_session, test_user.id)
    assert user.has_role(role)


def test_remove_role_from_user(db_session, test_user):
    """Test removing role from user."""
    # First, add a role
    role = UserRoleEnum.VOLUNTEER
    user_service.add_role_to_user(db_session, test_user.id, role)

    # Then remove it
    success = user_service.remove_role_from_user(db_session, test_user.id, role)

    assert success is True

    # Check the user object
    user = user_service.get_user(db_session, test_user.id)
    assert not user.has_role(role)


def test_create_user_with_existing_email(db_session, test_user):
    """Test that creating a user with an existing email raises an error."""
    user_data = create_random_user_data()
    user_data["email"] = test_user.email  # Use existing email
    user_schema = UserCreate(**user_data)

    with pytest.raises(ValueError, match="Email already registered"):
        user_service.create_user(db_session, user_schema)


def test_create_user_with_existing_phone(db_session, test_user):
    """Test that creating a user with an existing phone raises an error."""
    user_data = create_random_user_data()
    user_data["phone"] = test_user.phone  # Use existing phone
    user_schema = UserCreate(**user_data)

    with pytest.raises(ValueError, match="Phone number already registered"):
        user_service.create_user(db_session, user_schema)


def test_update_nonexistent_user(db_session):
    """Test updating a user that doesn't exist."""
    update_data = UserUpdate(full_name="New Name")
    updated_user = user_service.update_user(db_session, 9999, update_data)
    assert updated_user is None


def test_delete_user(db_session):
    """Test user deletion."""
    # Create a user to delete
    user_data = create_random_user_data()
    user_schema = UserCreate(**user_data)
    user = user_service.create_user(db_session, user_schema)

    # Delete the user
    success = user_service.delete_user(db_session, user.id)
    assert success is True

    # Verify user is gone
    deleted_user = user_service.get_user(db_session, user.id)
    assert deleted_user is None
