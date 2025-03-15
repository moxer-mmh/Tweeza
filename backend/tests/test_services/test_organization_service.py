import pytest
from app.services import organization_service
from app.schemas import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationMemberCreate,
    UserRoleEnum,
)
from app.db.models import Organization
from tests.utils import create_random_organization_data


def test_create_organization(db_session, test_admin_user):
    """Test organization creation."""
    org_data = create_random_organization_data()
    org_schema = OrganizationCreate(**org_data)

    org = organization_service.create_organization(
        db_session, org_schema, test_admin_user.id
    )

    assert org.name == org_data["name"]
    assert org.description == org_data["description"]

    # Check if creator is an admin of the organization
    members = organization_service.get_organization_members(db_session, org.id)
    assert any(
        m.user_id == test_admin_user.id and m.role == UserRoleEnum.ADMIN.value
        for m in members
    )


def test_get_organization(db_session, test_organization):
    """Test getting organization by ID."""
    org = organization_service.get_organization(db_session, test_organization.id)
    assert org is not None
    assert org.id == test_organization.id
    assert org.name == test_organization.name


def test_get_organization_by_name(db_session, test_organization):
    """Test getting organization by name."""
    org = organization_service.get_organization_by_name(
        db_session, test_organization.name
    )
    assert org is not None
    assert org.id == test_organization.id


def test_get_organizations(db_session, test_organization):
    """Test getting list of organizations."""
    orgs = organization_service.get_organizations(db_session)
    assert len(orgs) >= 1
    assert any(o.id == test_organization.id for o in orgs)


def test_update_organization(db_session, test_organization):
    """Test updating organization."""
    new_name = "Updated Organization Name"
    update_data = OrganizationUpdate(name=new_name)

    updated_org = organization_service.update_organization(
        db_session, test_organization.id, update_data
    )

    assert updated_org is not None
    assert updated_org.name == new_name


def test_create_organization_with_existing_name(
    db_session, test_organization, test_admin_user
):
    """Test that creating an organization with an existing name raises an error."""
    org_data = create_random_organization_data()
    org_data["name"] = test_organization.name  # Use existing name
    org_schema = OrganizationCreate(**org_data)

    with pytest.raises(ValueError, match="Organization with this name already exists"):
        organization_service.create_organization(
            db_session, org_schema, test_admin_user.id
        )


def test_add_member_to_organization(db_session, test_organization, test_user):
    """Test adding member to organization."""
    member_data = OrganizationMemberCreate(
        user_id=test_user.id, role=UserRoleEnum.WORKER
    )

    member = organization_service.add_member_to_organization(
        db_session, test_organization.id, member_data
    )

    assert member is not None
    assert member.user_id == test_user.id
    assert member.organization_id == test_organization.id
    assert member.role == UserRoleEnum.WORKER.value


def test_get_organization_members(db_session, test_organization, test_admin_user):
    """Test getting organization members."""
    members = organization_service.get_organization_members(
        db_session, test_organization.id
    )

    assert len(members) >= 1
    assert any(m.user_id == test_admin_user.id for m in members)


def test_get_user_organizations(db_session, test_organization, test_admin_user):
    """Test getting organizations for a user."""
    orgs = organization_service.get_user_organizations(db_session, test_admin_user.id)

    assert len(orgs) >= 1
    assert any(o.id == test_organization.id for o in orgs)


def test_remove_member_from_organization(db_session, test_organization, test_user):
    """Test removing member from organization."""
    # First, add a member
    member_data = OrganizationMemberCreate(
        user_id=test_user.id, role=UserRoleEnum.WORKER
    )
    organization_service.add_member_to_organization(
        db_session, test_organization.id, member_data
    )

    # Then remove them
    success = organization_service.remove_member_from_organization(
        db_session, test_organization.id, test_user.id
    )

    assert success is True

    # Check that they're no longer a member
    members = organization_service.get_organization_members(
        db_session, test_organization.id
    )
    assert not any(m.user_id == test_user.id for m in members)


def test_is_user_organization_admin(
    db_session, test_organization, test_admin_user, test_user
):
    """Test checking if user is admin of organization."""
    # Admin user should be admin
    is_admin = organization_service.is_user_organization_admin(
        db_session, test_admin_user.id, test_organization.id
    )
    assert is_admin is True

    # Regular user should not be admin
    is_admin = organization_service.is_user_organization_admin(
        db_session, test_user.id, test_organization.id
    )
    assert is_admin is False


def test_get_organization_admin(db_session, test_organization, test_admin_user):
    """Test getting organization admin."""
    admin = organization_service.get_organization_admin(
        db_session, test_organization.id
    )

    assert admin is not None
    assert admin.id == test_admin_user.id
