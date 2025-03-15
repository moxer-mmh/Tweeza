from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.db import get_db
from app.api.v1.dependencies import get_current_user
from app.services import analytics_service
from app.schemas import UserRoleEnum
from app.db.models import User

router = APIRouter()


@router.get("/dashboard")
def get_dashboard_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get analytics data for the dashboard.
    Only accessible to administrators and super admins.
    """
    # Check if user is admin or super admin
    if not (
        current_user.has_role(UserRoleEnum.ADMIN)
        or current_user.has_role(UserRoleEnum.SUPER_ADMIN)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access analytics",
        )

    # Get entity counts
    entity_counts = analytics_service.count_entities(db)

    # Get user registration trends
    registration_trend = analytics_service.user_registration_over_time(
        db, interval="week"
    )

    # Get role distribution
    role_distribution = analytics_service.user_roles_distribution(db)

    # Get geographical distribution
    geo_distribution = analytics_service.geographical_distribution(db)

    return {
        "entity_counts": entity_counts,
        "registration_trend": registration_trend,
        "role_distribution": role_distribution,
        "geo_distribution": geo_distribution,
    }


@router.get("/users/registrations")
def get_user_registrations(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    interval: str = Query("day", enum=["day", "week", "month"]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get user registration statistics over time.
    Only accessible to administrators and super admins.
    """
    # Check if user is admin or super admin
    if not (
        current_user.has_role(UserRoleEnum.ADMIN)
        or current_user.has_role(UserRoleEnum.SUPER_ADMIN)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access analytics",
        )

    registrations = analytics_service.user_registration_over_time(
        db, start_date, end_date, interval
    )

    return registrations


@router.get("/resources/contributions")
def get_resource_contributions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get resource contribution statistics by type.
    Only accessible to administrators and super admins.
    """
    # Check if user is admin or super admin
    if not (
        current_user.has_role(UserRoleEnum.ADMIN)
        or current_user.has_role(UserRoleEnum.SUPER_ADMIN)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access analytics",
        )

    contributions = analytics_service.resource_contributions_by_type(db)

    return contributions


@router.get("/events/attendance")
def get_event_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get event attendance statistics.
    Only accessible to administrators and super admins.
    """
    # Check if user is admin or super admin
    if not (
        current_user.has_role(UserRoleEnum.ADMIN)
        or current_user.has_role(UserRoleEnum.SUPER_ADMIN)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access analytics",
        )

    attendance_stats = analytics_service.event_attendance_stats(db)

    return attendance_stats
