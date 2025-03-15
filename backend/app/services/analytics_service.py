from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app.db.models import (
    User,
    Event,
    Organization,
    ResourceRequest,
    ResourceContribution,
    OrganizationMember,
    EventBeneficiary,  # Make sure this is imported/defined
    UserRole,  # Make sure this is imported/defined
)
from typing import Dict, List, Any, Optional


def count_entities(db: Session) -> Dict[str, int]:
    """
    Count the number of users, organizations, events, and resources.
    """
    return {
        "users": db.query(User).count(),
        "organizations": db.query(Organization).count(),
        "events": db.query(Event).count(),
        "resources": db.query(
            ResourceRequest
        ).count(),  # Changed from Resource to ResourceRequest
    }


def user_registration_over_time(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    interval: str = "day",
) -> List[Dict[str, Any]]:
    """
    Get user registration counts over time.

    Args:
        db: Database session
        start_date: Start date for the analysis (defaults to 30 days ago)
        end_date: End date for the analysis (defaults to today)
        interval: Time interval for grouping ("day", "week", "month")
    """
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()

    # Define date trunc function based on interval
    if interval == "week":
        date_trunc = func.date_trunc("week", User.created_at)
    elif interval == "month":
        date_trunc = func.date_trunc("month", User.created_at)
    else:
        date_trunc = func.date_trunc("day", User.created_at)

    # Query user registrations by date
    registrations = (
        db.query(date_trunc.label("date"), func.count(User.id).label("count"))
        .filter(User.created_at.between(start_date, end_date))
        .group_by("date")
        .order_by("date")
        .all()
    )

    # Format results
    return [
        {"date": date.strftime("%Y-%m-%d"), "count": count}
        for date, count in registrations
    ]


def resource_contributions_by_type(db: Session) -> List[Dict[str, Any]]:
    """
    Analyze resource contributions by resource type.
    """
    contributions = (
        db.query(
            ResourceRequest.resource_type,
            func.count(ResourceContribution.id).label(
                "count"
            ),  # Changed Resource to ResourceRequest
        )
        .join(
            ResourceContribution, ResourceRequest.id == ResourceContribution.request_id
        )  # Changed Resource.id to ResourceRequest.id and resource_id to request_id
        .group_by(ResourceRequest.resource_type)  # Changed Resource to ResourceRequest
        .all()
    )

    return [
        {"type": resource_type, "count": count}
        for resource_type, count in contributions
    ]


def event_attendance_stats(db: Session) -> Dict[str, Any]:
    """
    Get statistics about event attendance.
    """
    # Count total events
    total_events = db.query(Event).count()

    # Count total beneficiaries
    total_beneficiaries = (
        db.query(func.count(func.distinct(EventBeneficiary.user_id))).scalar() or 0
    )

    # Count average beneficiaries per event
    if total_events > 0:
        avg_beneficiaries_per_event = (
            db.query(func.avg(func.count(EventBeneficiary.user_id)))
            .group_by(EventBeneficiary.event_id)
            .scalar()
        ) or 0
    else:
        avg_beneficiaries_per_event = 0

    return {
        "total_events": total_events,
        "total_beneficiaries": total_beneficiaries,
        "avg_beneficiaries_per_event": float(avg_beneficiaries_per_event),
    }


def geographical_distribution(db: Session) -> List[Dict[str, Any]]:
    """
    Get geographical distribution of users.
    """
    user_locations = (
        db.query(User.location, func.count(User.id).label("count"))
        .filter(User.location != None, User.location != "")
        .group_by(User.location)
        .order_by(func.count(User.id).desc())
        .all()
    )

    return [
        {"location": location, "count": count} for location, count in user_locations
    ]


def user_roles_distribution(db: Session) -> List[Dict[str, Any]]:
    """
    Get distribution of user roles.
    """
    role_counts = (
        db.query(UserRole.role, func.count(UserRole.user_id).label("count"))
        .group_by(UserRole.role)
        .order_by(func.count(UserRole.user_id).desc())
        .all()
    )

    return [{"role": role, "count": count} for role, count in role_counts]


def get_event_statistics(db: Session) -> Dict[str, Any]:
    """
    Get comprehensive event statistics.
    """
    # Total events
    total_events = db.query(Event).count()

    # Events by organization
    events_by_org = (
        db.query(Organization.name, func.count(Event.id).label("count"))
        .join(Event, Organization.id == Event.organization_id)
        .group_by(Organization.id, Organization.name)
        .all()
    )

    return {
        "total_events": total_events,
        # Remove events_by_status since status field doesn't exist
        "events_by_organization": [
            {"organization": org, "count": count} for org, count in events_by_org
        ],
    }


def get_resource_statistics(db: Session) -> Dict[str, Any]:
    """
    Get comprehensive resource statistics.
    """
    # Total resource requests
    total_requests = db.query(ResourceRequest).count()

    # Total contributions
    total_contributions = db.query(ResourceContribution).count()

    # Resources by type
    resources_by_type = (
        db.query(
            ResourceRequest.resource_type, func.count(ResourceRequest.id).label("count")
        )
        .group_by(ResourceRequest.resource_type)
        .all()
    )

    # Fulfillment rate (received vs needed)
    fulfillment_data = db.query(
        func.sum(ResourceRequest.quantity_received).label("received"),
        func.sum(ResourceRequest.quantity_needed).label("needed"),
    ).first()

    fulfillment_rate = 0
    if fulfillment_data.needed and fulfillment_data.needed > 0:
        fulfillment_rate = (fulfillment_data.received or 0) / fulfillment_data.needed

    return {
        "total_requests": total_requests,
        "total_contributions": total_contributions,
        "resources_by_type": [
            {"type": res_type, "count": count} for res_type, count in resources_by_type
        ],
        "fulfillment_rate": fulfillment_rate,
    }
