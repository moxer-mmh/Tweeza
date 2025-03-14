import sys
import os
from sqlalchemy.orm import Session

# Add the project root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.session import DatabaseConnection
from app.db.models import User, UserRole
from app.schemas import UserRoleEnum
from app.core.security import get_password_hash


def create_super_admin(email: str, password: str, full_name: str, phone: str):
    """
    Create a super admin user.
    """
    db_instance = DatabaseConnection()
    db_instance.create_tables()  # Ensure tables are created

    session = db_instance.get_session()

    try:
        # Check if user exists
        existing_user = session.query(User).filter(User.email == email).first()

        if existing_user:
            # If user exists, add super_admin role if they don't have it
            existing_role = (
                session.query(UserRole)
                .filter(
                    UserRole.user_id == existing_user.id,
                    UserRole.role == UserRoleEnum.SUPER_ADMIN.value,
                )
                .first()
            )

            if existing_role:
                print(f"User {email} already exists and has super_admin role.")
                return

            # Add super_admin role
            super_admin_role = UserRole(
                user_id=existing_user.id, role=UserRoleEnum.SUPER_ADMIN.value
            )
            session.add(super_admin_role)
            session.commit()

            print(f"Added super_admin role to existing user {email}.")
        else:
            # Create new user
            new_user = User(
                email=email,
                phone=phone,
                password_hash=get_password_hash(password),
                full_name=full_name,
            )

            session.add(new_user)
            session.commit()
            session.refresh(new_user)

            # Add super_admin role
            super_admin_role = UserRole(
                user_id=new_user.id, role=UserRoleEnum.SUPER_ADMIN.value
            )
            session.add(super_admin_role)
            session.commit()

            print(f"Created new super admin user: {email}")

    finally:
        db_instance.close_session()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create a super admin user")
    parser.add_argument("--email", required=True, help="Email address")
    parser.add_argument("--password", required=True, help="Password")
    parser.add_argument("--full-name", required=True, help="Full name")
    parser.add_argument("--phone", required=True, help="Phone number")

    args = parser.parse_args()

    create_super_admin(args.email, args.password, args.full_name, args.phone)
