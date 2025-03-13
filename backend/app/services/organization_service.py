from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.db import Organization, Organizer, OrganizationMember, User
from app.schemas import OrganizationCreate


class OrganizationService:
    def __init__(self, db: Session):
        self.db = db

    def create_organization(
        self, org_data: OrganizationCreate, created_by_user_id: int
    ) -> Organization:
        """Create a new organization."""
        # Check for duplicate name
        existing = (
            self.db.query(Organization)
            .filter(Organization.name == org_data.name)
            .first()
        )
        if existing:
            raise ValueError("Organization with this name already exists")

        # Create organization
        organization = Organization(
            name=org_data.name,
            org_type=org_data.org_type,
            description=org_data.description,
            location=org_data.location,
            latitude=org_data.latitude,
            longitude=org_data.longitude,
            verified=False,  # New orgs are not verified by default
            created_by=created_by_user_id,
        )

        self.db.add(organization)
        self.db.commit()
        self.db.refresh(organization)

        # Create an organizer record for the creator
        self._add_organizer(organization.id, created_by_user_id, "Admin")

        return organization

    def get_organization_by_id(self, org_id: int) -> Optional[Organization]:
        """Get organization by ID with related data."""
        return (
            self.db.query(Organization)
            .options(
                joinedload(Organization.organizers).joinedload(Organizer.user),
                joinedload(Organization.members).joinedload(OrganizationMember.user),
            )
            .filter(Organization.id == org_id)
            .first()
        )

    def get_organizations(
        self,
        skip: int = 0,
        limit: int = 20,
        org_type: Optional[str] = None,
        verified_only: bool = False,
    ) -> List[Organization]:
        """Get organizations with filters."""
        query = self.db.query(Organization)

        if org_type:
            query = query.filter(Organization.org_type == org_type)

        if verified_only:
            query = query.filter(Organization.verified == True)

        return query.offset(skip).limit(limit).all()

    def update_organization(
        self, org_id: int, update_data: dict
    ) -> Optional[Organization]:
        """Update organization details."""
        organization = (
            self.db.query(Organization).filter(Organization.id == org_id).first()
        )
        if not organization:
            return None

        # Update organization fields
        for field, value in update_data.items():
            if hasattr(organization, field):
                setattr(organization, field, value)

        self.db.commit()
        self.db.refresh(organization)
        return organization

    def verify_organization(
        self, org_id: int, verified: bool = True
    ) -> Optional[Organization]:
        """Update verification status of an organization."""
        organization = (
            self.db.query(Organization).filter(Organization.id == org_id).first()
        )
        if not organization:
            return None

        organization.verified = verified
        self.db.commit()
        self.db.refresh(organization)
        return organization

    def add_member(
        self, org_id: int, user_id: int, role: str = "Member"
    ) -> OrganizationMember:
        """Add a member to an organization."""
        # Check if already a member
        existing = (
            self.db.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.user_id == user_id,
            )
            .first()
        )

        if existing:
            # Update role if already a member
            existing.role = role
            self.db.commit()
            self.db.refresh(existing)
            return existing

        # Add new member
        member = OrganizationMember(organization_id=org_id, user_id=user_id, role=role)

        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def _add_organizer(self, org_id: int, user_id: int, role: str) -> Organizer:
        """Add an organizer for an organization (internal method)."""
        # Make sure user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        # Check if already an organizer for this organization
        existing = (
            self.db.query(Organizer)
            .filter(Organizer.organization_id == org_id, Organizer.user_id == user_id)
            .first()
        )

        if existing:
            existing.role = role
            self.db.commit()
            return existing

        # Create new organizer record
        organizer = Organizer(user_id=user_id, organization_id=org_id, role=role)

        self.db.add(organizer)
        self.db.commit()
        self.db.refresh(organizer)
        return organizer
