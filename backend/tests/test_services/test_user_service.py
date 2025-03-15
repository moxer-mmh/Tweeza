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


def test_get_user_by_id_not_found(db_session):
    """Test getting a non-existent user by ID."""
    user = user_service.get_user(db_session, 999999)  # Non-existent ID
    assert user is None


def test_get_users_empty(db_session):
    """Test getting users when there are none."""
    # Clear all users first (only in test environment)
    db_session.query(UserRole).delete()
    db_session.query(User).delete()
    db_session.commit()

    users = user_service.get_users(db_session)
    assert len(users) == 0


def test_update_user_not_found(db_session):
    """Test updating a non-existent user."""
    update_data = UserUpdate(full_name="New Name")
    updated_user = user_service.update_user(db_session, 999999, update_data)
    assert updated_user is None


def test_add_role_to_user_multiple_roles(db_session, test_user):
    """Test adding multiple roles to a user."""
    # First role
    role1 = UserRoleEnum.VOLUNTEER
    user_role1 = user_service.add_role_to_user(db_session, test_user.id, role1)
    assert user_role1 is not None
    assert user_role1.role == role1.value

    # Second role
    role2 = UserRoleEnum.WORKER
    user_role2 = user_service.add_role_to_user(db_session, test_user.id, role2)
    assert user_role2 is not None
    assert user_role2.role == role2.value

    # Check the user object has both roles
    user = user_service.get_user(db_session, test_user.id)
    assert user.has_role(role1)
    assert user.has_role(role2)


def test_add_role_to_user_already_exists(db_session, test_user):
    """Test adding a role that the user already has."""
    # First add the role
    role = UserRoleEnum.VOLUNTEER
    user_service.add_role_to_user(db_session, test_user.id, role)

    # Add the same role again
    user_role = user_service.add_role_to_user(db_session, test_user.id, role)

    # Should return the existing role
    assert user_role is not None
    assert user_role.role == role.value


def test_add_role_to_user_nonexistent_user(db_session):
    """Test adding a role to a non-existent user."""
    role = UserRoleEnum.VOLUNTEER
    user_role = user_service.add_role_to_user(db_session, 999999, role)
    assert user_role is None


def test_remove_role_from_user_nonexistent_user(db_session):
    """Test removing a role from a non-existent user."""
    role = UserRoleEnum.VOLUNTEER
    success = user_service.remove_role_from_user(db_session, 999999, role)
    assert success is False


def test_remove_role_from_user_nonexistent_role(db_session, test_user):
    """Test removing a role that the user doesn't have."""
    # Make sure user doesn't have the role
    role = UserRoleEnum.SUPER_ADMIN
    db_session.query(UserRole).filter(
        UserRole.user_id == test_user.id, UserRole.role == role.value
    ).delete()
    db_session.commit()

    success = user_service.remove_role_from_user(db_session, test_user.id, role)
    assert success is False


def test_count_users_with_role(db_session, test_user):
    """Test counting users with a specific role."""
    # Add a role to the test user
    role = UserRoleEnum.VOLUNTEER
    user_service.add_role_to_user(db_session, test_user.id, role)

    # Count users with this role
    count = user_service.count_users_with_role(db_session, role)
    assert count >= 1


def test_get_organization_users(db_session, test_user):
    """Test getting users from organizations."""
    from app.db.models import Organization, OrganizationMember

    # Create a test organization
    org = Organization(name="Test Org", description="Test Description")
    db_session.add(org)
    db_session.commit()

    # Add test user to the organization
    member = OrganizationMember(
        user_id=test_user.id, organization_id=org.id, role=UserRoleEnum.ADMIN.value
    )
    db_session.add(member)
    db_session.commit()

    # Test get_organization_users
    users = user_service.get_organization_users(db_session, [org.id])
    assert len(users) >= 1
    assert any(u.id == test_user.id for u in users)


def test_get_user_organizations(db_session, test_user):
    """Test getting organizations for a user."""
    from app.db.models import Organization, OrganizationMember

    # Create a test organization
    org = Organization(name="Test Org 2", description="Test Description")
    db_session.add(org)
    db_session.commit()

    # Add test user to the organization
    member = OrganizationMember(
        user_id=test_user.id, organization_id=org.id, role=UserRoleEnum.ADMIN.value
    )
    db_session.add(member)
    db_session.commit()

    # Test get_user_organizations
    orgs = user_service.get_user_organizations(db_session, test_user.id)
    assert len(orgs) >= 1
    assert any(o.id == org.id for o in orgs)
