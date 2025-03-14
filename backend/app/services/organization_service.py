from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models import Organization, OrganizationMember, User
from app.schemas import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationMemberCreate,
    UserRoleEnum,
)


def get_organization(db: Session, org_id: int) -> Optional[Organization]:
    """Get an organization by ID."""
    return db.query(Organization).filter(Organization.id == org_id).first()


def get_organization_by_name(db: Session, name: str) -> Optional[Organization]:
    """Get an organization by name."""
    return db.query(Organization).filter(Organization.name == name).first()


def get_organizations(
    db: Session, skip: int = 0, limit: int = 100
) -> List[Organization]:
    """Get all organizations with pagination."""
    return db.query(Organization).offset(skip).limit(limit).all()


def create_organization(
    db: Session, org_data: OrganizationCreate, creator_id: int
) -> Organization:
    """Create a new organization."""
    # Check if organization exists
    if get_organization_by_name(db, org_data.name):
        raise ValueError("Organization with this name already exists")

    # Create organization
    db_org = Organization(
        name=org_data.name,
        description=org_data.description,
        location=org_data.location,
        latitude=org_data.latitude,
        longitude=org_data.longitude,
    )

    db.add(db_org)
    db.commit()
    db.refresh(db_org)

    # Add creator as admin
    member = OrganizationMember(
        organization_id=db_org.id, user_id=creator_id, role=UserRoleEnum.ADMIN.value
    )

    db.add(member)
    db.commit()

    return db_org


def update_organization(
    db: Session, org_id: int, org_data: OrganizationUpdate
) -> Optional[Organization]:
    """Update an organization."""
    db_org = get_organization(db, org_id)
    if not db_org:
        return None

    # Update fields if provided
    update_data = org_data.model_dump(exclude_unset=True)

    # If name is being updated, check it doesn't conflict
    if "name" in update_data:
        existing = get_organization_by_name(db, update_data["name"])
        if existing and existing.id != org_id:
            raise ValueError("Organization with this name already exists")

    for field, value in update_data.items():
        setattr(db_org, field, value)

    db.commit()
    db.refresh(db_org)
    return db_org


def delete_organization(db: Session, org_id: int) -> bool:
    """Delete an organization."""
    db_org = get_organization(db, org_id)
    if not db_org:
        return False

    db.delete(db_org)
    db.commit()
    return True


def add_member_to_organization(
    db: Session, org_id: int, member_data: OrganizationMemberCreate
) -> Optional[OrganizationMember]:
    """Add a member to an organization."""
    # Check if organization exists
    db_org = get_organization(db, org_id)
    if not db_org:
        return None

    # Check if user exists
    user = db.query(User).filter(User.id == member_data.user_id).first()
    if not user:
        return None

    # Check if already a member
    existing_member = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == member_data.user_id,
        )
        .first()
    )

    if existing_member:
        return existing_member

    # Add new member
    member = OrganizationMember(
        organization_id=org_id, user_id=member_data.user_id, role=member_data.role
    )

    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def remove_member_from_organization(db: Session, org_id: int, user_id: int) -> bool:
    """Remove a member from an organization."""
    member = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == user_id,
        )
        .first()
    )

    if not member:
        return False

    db.delete(member)
    db.commit()
    return True


def get_organization_members(db: Session, org_id: int) -> List[OrganizationMember]:
    """Get all members of an organization."""
    return (
        db.query(OrganizationMember)
        .filter(OrganizationMember.organization_id == org_id)
        .all()
    )


def get_user_organizations(db: Session, user_id: int) -> List[Organization]:
    """Get all organizations for a user."""
    memberships = (
        db.query(OrganizationMember).filter(OrganizationMember.user_id == user_id).all()
    )

    org_ids = [m.organization_id for m in memberships]
    return db.query(Organization).filter(Organization.id.in_(org_ids)).all()
