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


def can_manage_user(user: User, target_user_id: int, db: Session) -> bool:
    """
    Check if a user can manage another user.

    Super admins can manage any user.
    Organization admins can manage users in their organization.
    Regular users can only manage themselves.
    """
    # Super admins can manage any user
    if is_super_admin(user):
        return True

    # Users can manage themselves
    if user.id == target_user_id:
        return True

    # Check if user is an organization admin
    if user.has_role(UserRoleEnum.ADMIN.value):
        # Get organizations where the user is admin
        from app.db.models import OrganizationMember, Organization

        # Get orgs where user is admin
        admin_orgs = (
            db.query(Organization)
            .join(OrganizationMember)
            .filter(
                OrganizationMember.user_id == user.id,
                OrganizationMember.role == UserRoleEnum.ADMIN.value,
            )
            .all()
        )

        # Get org IDs
        admin_org_ids = [org.id for org in admin_orgs]
        if not admin_org_ids:
            return False

        # Check if target user is in any of these orgs
        target_is_member = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.user_id == target_user_id,
                OrganizationMember.organization_id.in_(admin_org_ids),
            )
            .first()
        )

        return target_is_member is not None

    # Regular users can only manage themselves
    return False
