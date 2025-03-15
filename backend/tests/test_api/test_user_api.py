import pytest
from fastapi import status
from tests.utils import create_random_user_data
from app.db.models import User, UserRole, OrganizationMember
from app.schemas import UserRoleEnum


def test_read_current_user(client, token_headers, test_user):
    """Test getting current user information."""
    response = client.get("/api/v1/users/me", headers=token_headers)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name


def test_read_current_user_unauthorized(client):
    """Test accessing current user without authentication."""
    response = client.get("/api/v1/users/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_user(client, token_headers, test_user):
    """Test updating user information."""
    new_name = "Updated Test User"
    update_data = {"full_name": new_name}

    response = client.put(
        f"/api/v1/users/{test_user.id}", json=update_data, headers=token_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["full_name"] == new_name


def test_update_other_user_as_regular_user(client, token_headers, test_admin_user):
    """Test that a regular user cannot update another user."""
    update_data = {"full_name": "Should Not Update"}

    response = client.put(
        f"/api/v1/users/{test_admin_user.id}", json=update_data, headers=token_headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_user_as_admin(
    client, admin_token_headers, test_user, test_organization
):
    """Test that an admin can update another user."""
    new_name = "Admin Updated User"
    update_data = {"full_name": new_name}

    response = client.put(
        f"/api/v1/users/{test_user.id}", json=update_data, headers=admin_token_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["full_name"] == new_name


def test_update_user_as_super_admin(client, super_admin_token_headers, test_user):
    """Test that a super admin can update any user."""
    new_name = "Super Admin Updated User"
    update_data = {"full_name": new_name}

    response = client.put(
        f"/api/v1/users/{test_user.id}",
        json=update_data,
        headers=super_admin_token_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["full_name"] == new_name


def test_get_user(client, token_headers, test_user):
    """Test getting user by ID."""
    response = client.get(f"/api/v1/users/{test_user.id}", headers=token_headers)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email


def test_list_users_as_regular_user(client, token_headers):
    """Test that regular users cannot list all users."""
    response = client.get("/api/v1/users/", headers=token_headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_users_as_admin(client, admin_token_headers):
    """Test that admins can list users in their organization."""
    response = client.get("/api/v1/users/", headers=admin_token_headers)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)


def test_list_users_as_super_admin(client, super_admin_token_headers):
    """Test that super admins can list all users."""
    response = client.get("/api/v1/users/", headers=super_admin_token_headers)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)
    # Check that we get at least one user (the super_admin themselves)
    assert len(data) >= 1

    # Check that the super admin is in the response
    assert any(user["email"] == "superadmin@example.com" for user in data)


def test_add_role_to_user(client, token_headers, test_user):
    """Test adding a role to own user profile."""
    role_data = {"role": "volunteer"}

    response = client.post(
        f"/api/v1/users/{test_user.id}/roles", json=role_data, headers=token_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert any(role["role"] == "volunteer" for role in data["roles"])


def test_add_admin_role_as_regular_user(client, token_headers, test_user):
    """Test that regular users cannot add admin roles."""
    role_data = {"role": "admin"}

    response = client.post(
        f"/api/v1/users/{test_user.id}/roles", json=role_data, headers=token_headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_remove_role_from_user(client, token_headers, test_user):
    """Test removing a role from a user."""
    # First add a role
    role_data = {"role": "volunteer"}
    client.post(
        f"/api/v1/users/{test_user.id}/roles", json=role_data, headers=token_headers
    )

    # Then remove it
    response = client.delete(
        f"/api/v1/users/{test_user.id}/roles/volunteer", headers=token_headers
    )

    assert response.status_code == status.HTTP_200_OK


def test_delete_user_as_regular_user(
    client, normal_user_token_headers, test_user2, db_session
):
    """Test regular users can only delete themselves."""
    # Update the test to use a direct test_user2 ID comparison
    user_id = normal_user_token_headers.get("X-Test-User-ID")

    # First ensure normal_user_token_headers user isn't test_user2
    if str(test_user2.id) == user_id:
        # Create a different user
        from app.db.models import User
        from app.core.security import get_password_hash

        new_user = User(
            email="another_test_user@example.com",
            password_hash=get_password_hash("password"),
            phone="555123456",
            full_name="Another Test User",
        )
        db_session.add(new_user)
        db_session.commit()
        test_user2 = new_user

    # Attempt to delete another user - should be forbidden
    response = client.delete(
        f"/api/v1/users/{test_user2.id}", headers=normal_user_token_headers
    )
    assert response.status_code == 403

    # Test user can delete themselves
    if user_id:
        response = client.delete(
            f"/api/v1/users/{user_id}", headers=normal_user_token_headers
        )
        assert response.status_code == 200


# def test_delete_user_as_admin(
#     client, admin_token_headers, test_user2, test_organization, db_session
# ):
#     """Test admin can delete users."""
#     # Ensure test_user2 is in test_organization and admin has permissions
    
#     # Get admin user
#     admin_user = db_session.query(User).filter(User.email == "admin@example.com").first()
    
#     if not admin_user:
#         pytest.skip("No admin user found")
        
#     # Make sure admin has admin role
#     admin_role = db_session.query(UserRole).filter(
#         UserRole.user_id == admin_user.id,
#         UserRole.role == UserRoleEnum.ADMIN.value
#     ).first()
    
#     if not admin_role:
#         new_role = UserRole(user_id=admin_user.id, role=UserRoleEnum.ADMIN.value)
#         db_session.add(new_role)
#         db_session.commit()
    
#     # Ensure test_user2 is in organization
#     org_member = (
#         db_session.query(OrganizationMember)
#         .filter(
#             OrganizationMember.organization_id == test_organization.id,
#             OrganizationMember.user_id == test_user2.id
#         )
#         .first()
#     )
    
#     if not org_member:
#         org_member = OrganizationMember(
#             organization_id=test_organization.id,
#             user_id=test_user2.id,
#             role=UserRoleEnum.WORKER.value
#         )
#         db_session.add(org_member)
#         db_session.commit()

#     # Now try delete
#     response = client.delete(
#         f"/api/v1/users/{test_user2.id}", headers=admin_token_headers
#     )
#     assert response.status_code == 200
#     assert response.json() == {"message": "User deleted successfully"}


def test_delete_nonexistent_user(client, admin_token_headers):
    """Test deleting a user that doesn't exist."""
    response = client.delete("/api/v1/users/99999", headers=admin_token_headers)
    assert response.status_code == 404


def test_search_users(client, superadmin_token_headers, test_user, test_admin_user):
    """Test searching users by name or email."""
    # Search by part of email
    response = client.get(
        f"/api/v1/users/search?query={test_user.email[:5]}",
        headers=superadmin_token_headers,
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1

    # Search by part of name
    name_part = test_admin_user.full_name.split()[0]
    response = client.get(
        f"/api/v1/users/search?query={name_part}", headers=superadmin_token_headers
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


# def test_get_user_count_by_role(client, superadmin_token_headers):
#     """Test getting user count by role."""
#     response = client.get(
#         "/api/v1/users/count-by-role?role=admin", headers=superadmin_token_headers
#     )
#     assert response.status_code == 200
#     assert "count" in response.json()
#     assert response.json()["count"] >= 1

#     # Test with invalid role
#     response = client.get(
#         "/api/v1/users/count-by-role?role=invalid_role",
#         headers=superadmin_token_headers,
#     )
#     assert response.status_code == 422


def test_get_user_roles(client, admin_token_headers, test_admin_user):
    """Test getting user roles."""
    response = client.get(
        f"/api/v1/users/{test_admin_user.id}/roles", headers=admin_token_headers
    )
    assert response.status_code == 200
    roles = response.json()
    assert len(roles) >= 1
    assert "admin" in [role["role"] for role in roles]


# def test_get_users_with_role(client, superadmin_token_headers):
#     """Test getting users with a specific role."""
#     response = client.get(
#         "/api/v1/users/with-role/admin", headers=superadmin_token_headers
#     )
#     assert response.status_code == 200
#     users = response.json()
#     assert len(users) >= 1
