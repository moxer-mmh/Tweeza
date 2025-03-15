#!/usr/bin/env python3
"""
Script to create a super admin user for Tweeza platform.
"""
import sys
import argparse
from pathlib import Path
import os

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas import UserRoleEnum
from app.services import user_service
from app.core.security import get_password_hash
from app.db.models import User, UserRole


def setup_argparse():
    """Configure the argument parser."""
    parser = argparse.ArgumentParser(description="Create a super admin user")

    parser.add_argument("--email", required=True, help="Admin email address")
    parser.add_argument("--password", required=True, help="Admin password")
    parser.add_argument("--name", required=True, help="Admin full name")
    parser.add_argument("--phone", required=True, help="Admin phone number")
    parser.add_argument("--location", default="Default Location", help="Admin location")
    parser.add_argument(
        "--latitude", type=float, default=0.0, help="Latitude coordinate"
    )
    parser.add_argument(
        "--longitude", type=float, default=0.0, help="Longitude coordinate"
    )

    return parser


def create_super_admin(db: Session, args):
    """Create a super admin user or add super admin role to existing user."""
    # Check if user exists
    user = user_service.get_user_by_email(db, args.email)

    if not user:
        # Create new user
        user = User(
            email=args.email,
            full_name=args.name,
            password_hash=get_password_hash(args.password),
            phone=args.phone,
            location=args.location,
            latitude=args.latitude,
            longitude=args.longitude,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created new user: {user.email}")
    else:
        print(f"User {user.email} already exists")

    # Check if user already has super admin role
    super_admin_role = (
        db.query(UserRole)
        .filter(
            UserRole.user_id == user.id, UserRole.role == UserRoleEnum.SUPER_ADMIN.value
        )
        .first()
    )

    if not super_admin_role:
        # Add super admin role
        new_role = UserRole(user_id=user.id, role=UserRoleEnum.SUPER_ADMIN.value)
        db.add(new_role)
        db.commit()
        print(f"Super admin role added to user {user.email}")
        return f"Super admin user {user.email} created successfully."
    else:
        print(f"User {user.email} already has super admin role")
        return f"Added super admin role to existing user {user.email}."


def main():
    """Main function to create a super admin user."""
    parser = setup_argparse()
    args = parser.parse_args()

    try:
        db = SessionLocal()
        result = create_super_admin(db, args)
        print(result)
    except Exception as e:
        print(f"Error creating super admin: {str(e)}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
