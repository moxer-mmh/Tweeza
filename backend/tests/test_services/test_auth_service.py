import pytest
from app.services import auth_service
from app.schemas import UserLogin, UserRoleEnum
from app.core.security import decode_token
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
