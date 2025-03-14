from sqlalchemy.orm import Session
from typing import Optional
from app.db.models import User
from app.core.security import verify_password, create_access_token
from app.schemas import Token, UserLogin, UserRoleEnum
from datetime import timedelta
from app.core.config import settings
from app.services import user_service, organization_service


def authenticate_user(db: Session, auth_data: UserLogin) -> Optional[User]:
    """Authenticate a user with email and password."""
    user = user_service.get_user_by_email(db, auth_data.email)

    if not user:
        return None

    if not verify_password(auth_data.password, user.password_hash):
        return None

    return user


def create_user_token(user_id: int) -> Token:
    """Create an access token for the user."""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user_id, expires_delta=access_token_expires
    )
    return Token(access_token=access_token)


def check_user_role(user: User, required_role: UserRoleEnum) -> bool:
    """Check if the user has a specific role."""
    return user.has_role(required_role)


def is_super_admin(user: User) -> bool:
    """Check if the user is a super admin."""
    return user.has_role(UserRoleEnum.SUPER_ADMIN.value)


def can_manage_organization(user: User, org_id: int, db: Session) -> bool:
    """
    Check if the user can manage the organization.
    Super admins can manage all organizations.
    Org admins can only manage their own organizations.
    """
    from app.services import organization_service

    # Super admins can manage all organizations
    if is_super_admin(user):
        return True

    # Check if user is an admin of this specific organization
    return organization_service.is_user_organization_admin(db, user.id, org_id)


def can_manage_user(admin_user: User, target_user_id: int, db: Session) -> bool:
    """
    Check if the admin user can manage the target user.
    Super admins can manage all users.
    Organization admins can only manage users in their organizations.
    """
    # Super admins can manage all users
    if is_super_admin(admin_user):
        return True

    # Get all organizations where the admin is an admin
    admin_orgs = organization_service.get_user_organizations(db, admin_user.id)
    admin_org_ids = [
        org.id
        for org in admin_orgs
        if any(
            m.role == UserRoleEnum.ADMIN.value
            for m in org.members
            if m.user_id == admin_user.id
        )
    ]

    # Check if target user is in any of the admin's organizations
    for org_id in admin_org_ids:
        members = organization_service.get_organization_members(db, org_id)
        if any(m.user_id == target_user_id for m in members):
            return True

    return False
