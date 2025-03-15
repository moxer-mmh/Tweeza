import pytest
from app.services import auth_service, user_service
from app.schemas import UserLogin, UserRoleEnum, UserCreate
from app.core.security import decode_token
from app.db.models import User, Organization, OrganizationMember, UserRole
from datetime import timedelta


def test_authenticate_user_success(db_session, test_user):
    """Test successful user authentication."""
    login_data = UserLogin(email=test_user.email, password="password")
    authenticated_user = auth_service.authenticate_user(db_session, login_data)

    assert authenticated_user is not None
    assert authenticated_user.id == test_user.id


def test_authenticate_user_wrong_password(db_session, test_user):
    """Test authentication with wrong password."""
    login_data = UserLogin(email=test_user.email, password="wrong_password")
    authenticated_user = auth_service.authenticate_user(db_session, login_data)

    assert authenticated_user is None


def test_authenticate_user_nonexistent(db_session):
    """Test authentication with non-existent user."""
    login_data = UserLogin(email="nonexistent@example.com", password="password")
    authenticated_user = auth_service.authenticate_user(db_session, login_data)

    assert authenticated_user is None


def test_create_user_token(test_user):
    """Test token creation."""
    token = auth_service.create_user_token(test_user.id)

    assert token is not None
    assert token.access_token is not None

    # Verify token contains user ID
    payload = decode_token(token.access_token)
    assert payload is not None
    assert int(payload["sub"]) == test_user.id


def test_check_user_role(test_admin_user):
    """Test checking if user has a specific role."""
    # Admin should have ADMIN role
    has_role = auth_service.check_user_role(test_admin_user, UserRoleEnum.ADMIN)
    assert has_role is True

    # Admin should not have SUPER_ADMIN role
    has_role = auth_service.check_user_role(test_admin_user, UserRoleEnum.SUPER_ADMIN)
    assert has_role is False


def test_is_super_admin(test_user, test_super_admin):
    """Test checking if user is super admin."""
    # Regular user is not super admin
    is_super = auth_service.is_super_admin(test_user)
    assert is_super is False

    # Super admin user is super admin
    is_super = auth_service.is_super_admin(test_super_admin)
    assert is_super is True


def test_can_manage_organization(
    db_session, test_user, test_admin_user, test_super_admin, test_organization
):
    """Test checking if user can manage an organization."""
    # Super admin can manage any organization
    can_manage = auth_service.can_manage_organization(
        test_super_admin, test_organization.id, db_session
    )
    assert can_manage is True

    # Organization admin can manage their organization
    can_manage = auth_service.can_manage_organization(
        test_admin_user, test_organization.id, db_session
    )
    assert can_manage is True

    # Regular user cannot manage organization
    can_manage = auth_service.can_manage_organization(
        test_user, test_organization.id, db_session
    )
    assert can_manage is False


def test_user_has_role_method(db_session, test_admin_user):
    """Test the has_role method on the User model directly."""
    # Admin user should have ADMIN role
    assert test_admin_user.has_role(UserRoleEnum.ADMIN) is True

    # Admin user should not have SUPER_ADMIN role
    assert test_admin_user.has_role(UserRoleEnum.SUPER_ADMIN) is False

    # Test with string value
    assert test_admin_user.has_role("admin") is True
    assert test_admin_user.has_role("super_admin") is False


def test_can_manage_user_super_admin(db_session, test_user):
    """Test super admin can manage any user."""
    # Create a new test user to manage
    user_data = {
        "email": "managed_user@example.com",
        "phone": "9876543210",
        "password": "testpass123",
        "full_name": "Managed User",
        "location": "Test Location",
        "roles": [],
    }
    managed_user = user_service.create_user(db_session, UserCreate(**user_data))

    # Make test_user a super_admin
    user_service.add_role_to_user(db_session, test_user.id, UserRoleEnum.SUPER_ADMIN)

    # Test that super admin can manage any user
    assert auth_service.can_manage_user(test_user, managed_user.id, db_session) is True


def test_can_manage_user_self(db_session, test_user):
    """Test user can manage themselves."""
    # User should be able to manage their own profile
    assert auth_service.can_manage_user(test_user, test_user.id, db_session) is True


def test_can_manage_user_admin_can_manage_org_member(db_session, test_user):
    """Test org admin can manage users in their organization."""
    # Create a new test user to manage
    user_data = {
        "email": "org_member@example.com",
        "phone": "1230987654",
        "password": "testpass123",
        "full_name": "Org Member",
        "location": "Test Location",
        "roles": [],
    }
    managed_user = user_service.create_user(db_session, UserCreate(**user_data))

    # Make test_user an admin
    user_service.add_role_to_user(db_session, test_user.id, UserRoleEnum.ADMIN)

    # Create an organization
    org = Organization(name="Test Org", description="Test Description")
    db_session.add(org)
    db_session.commit()

    # Add test_user as an admin of the organization
    admin_member = OrganizationMember(
        user_id=test_user.id, organization_id=org.id, role=UserRoleEnum.ADMIN.value
    )
    db_session.add(admin_member)

    # Add managed_user as a regular member of the organization
    member = OrganizationMember(
        user_id=managed_user.id, organization_id=org.id, role=UserRoleEnum.WORKER.value
    )
    db_session.add(member)
    db_session.commit()

    # Test that admin can manage user in the same organization
    assert auth_service.can_manage_user(test_user, managed_user.id, db_session) is True


def test_can_manage_user_admin_cannot_manage_outside_org(db_session, test_user):
    """Test org admin cannot manage users outside their organization."""
    # Create a new test user to manage
    user_data = {
        "email": "outside_user@example.com",
        "phone": "5556667777",
        "password": "testpass123",
        "full_name": "Outside User",
        "location": "Test Location",
        "roles": [],
    }
    outside_user = user_service.create_user(db_session, UserCreate(**user_data))

    # Make test_user an admin
    user_service.add_role_to_user(db_session, test_user.id, UserRoleEnum.ADMIN)

    # Create an organization
    org = Organization(name="Test Org", description="Test Description")
    db_session.add(org)
    db_session.commit()

    # Add test_user as an admin of the organization
    admin_member = OrganizationMember(
        user_id=test_user.id, organization_id=org.id, role=UserRoleEnum.ADMIN.value
    )
    db_session.add(admin_member)
    db_session.commit()

    # outside_user is not in the organization

    # Test that admin cannot manage user outside the organization
    assert auth_service.can_manage_user(test_user, outside_user.id, db_session) is False


def test_can_manage_user_non_admin_cannot_manage_others(db_session, test_user):
    """Test non-admin users cannot manage other users."""
    # Create a new test user to manage
    user_data = {
        "email": "another_user@example.com",
        "phone": "1112223333",
        "password": "testpass123",
        "full_name": "Another User",
        "location": "Test Location",
        "roles": [],
    }
    another_user = user_service.create_user(db_session, UserCreate(**user_data))

    # Make sure test_user is not an admin or super_admin
    # Direct deletion from UserRole table instead of using joins
    for role in [UserRoleEnum.ADMIN, UserRoleEnum.SUPER_ADMIN]:
        db_session.query(UserRole).filter(
            UserRole.user_id == test_user.id, UserRole.role == role.value
        ).delete()
    db_session.commit()

    # Test that non-admin cannot manage other users
    assert auth_service.can_manage_user(test_user, another_user.id, db_session) is False
