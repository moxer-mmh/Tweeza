from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Float, text
from typing import List, Optional, Dict, Any
from app.db.models import (
    Event,
    ResourceRequest,
    User,
    Organization,
)
import math


def search_users(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 20,
    filters: Optional[Dict[str, Any]] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "asc",
) -> List[User]:
    """
    Search for users by name or email.
    """
    search_query = db.query(User).filter(
        func.lower(User.full_name).contains(func.lower(query))
        | func.lower(User.email).contains(func.lower(query))
    )

    # Apply additional filters
    if filters:
        for field, value in filters.items():
            if hasattr(User, field):
                search_query = search_query.filter(getattr(User, field) == value)

    # Apply sorting
    if sort_by and hasattr(User, sort_by):
        sort_attr = getattr(User, sort_by)
        if sort_order.lower() == "desc":
            sort_attr = sort_attr.desc()
        search_query = search_query.order_by(sort_attr)

    return search_query.offset(skip).limit(limit).all()


def search_organizations(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 20,
    filters: Optional[Dict[str, Any]] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "asc",
) -> List[Organization]:
    """
    Search for organizations by name or description.
    """
    search_query = db.query(Organization).filter(
        func.lower(Organization.name).contains(func.lower(query))
        | func.lower(Organization.description).contains(func.lower(query))
    )

    # Apply additional filters
    if filters:
        for field, value in filters.items():
            if hasattr(Organization, field):
                search_query = search_query.filter(
                    getattr(Organization, field) == value
                )

    # Apply sorting
    if sort_by and hasattr(Organization, sort_by):
        sort_attr = getattr(Organization, sort_by)
        if sort_order.lower() == "desc":
            sort_attr = sort_attr.desc()
        search_query = search_query.order_by(sort_attr)

    return search_query.offset(skip).limit(limit).all()


def search_events(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 20,
    filters: Optional[Dict[str, Any]] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "asc",
) -> List[Event]:
    """
    Search for events by title.
    """
    search_query = db.query(Event).filter(
        func.lower(Event.title).contains(func.lower(query))
    )

    # Apply additional filters
    if filters:
        for field, value in filters.items():
            if hasattr(Event, field):
                search_query = search_query.filter(getattr(Event, field) == value)

    # Apply sorting
    if sort_by and hasattr(Event, sort_by):
        sort_attr = getattr(Event, sort_by)
        if sort_order.lower() == "desc":
            sort_attr = sort_attr.desc()
        search_query = search_query.order_by(sort_attr)

    return search_query.offset(skip).limit(limit).all()


def global_search(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 20,
) -> Dict[str, List]:
    """
    Search across all entity types.
    Returns dictionary with results for each entity type.
    """
    # For a global search, we'll divide the limit across entity types
    per_type_limit = max(5, limit // 3)

    return {
        "users": search_users(db, query, skip, per_type_limit),
        "organizations": search_organizations(db, query, skip, per_type_limit),
        "events": search_events(db, query, skip, per_type_limit),
    }


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points
    on the earth using the Haversine formula.
    Returns distance in kilometers.
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r


def full_text_search_resources(
    db: Session,
    query: str,
    resource_type: Optional[str] = None,
    organization_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[ResourceRequest]:
    """
    Perform full-text search on resources.
    """
    search_query = db.query(ResourceRequest).filter(
        func.lower(ResourceRequest.name).contains(func.lower(query))
        | func.lower(ResourceRequest.description).contains(func.lower(query))
    )

    if resource_type:
        search_query = search_query.filter(
            ResourceRequest.resource_type == resource_type
        )

    if organization_id:
        search_query = search_query.filter(
            ResourceRequest.organization_id == organization_id
        )

    return search_query.offset(skip).limit(limit).all()


def geospatial_search_events(
    db: Session,
    latitude: float,
    longitude: float,
    radius: float = 10.0,  # Default 10km radius
    event_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """
    Find events within a certain radius using more efficient SQL-based calculation.
    Returns events with calculated distance.
    """
    # Base query
    query = db.query(Event)

    # Apply filters
    if event_type:
        query = query.filter(Event.event_type == event_type)

    if start_date:
        query = query.filter(Event.start_time >= start_date)

    if end_date:
        query = query.filter(Event.end_time <= end_date)

    # Get all events with coordinates
    events_with_coords = query.filter(
        Event.latitude.isnot(None), Event.longitude.isnot(None)
    ).all()

    # Calculate distance for each event
    result = []
    for event in events_with_coords:
        distance = calculate_distance(
            latitude, longitude, event.latitude, event.longitude
        )
        if distance <= radius:
            event_dict = {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "start_time": event.start_time,
                "end_time": event.end_time,
                "event_type": event.event_type,
                "organization_id": event.organization_id,
                "address": event.address,
                "latitude": event.latitude,
                "longitude": event.longitude,
                "distance_km": round(distance, 2),
            }
            result.append(event_dict)

    # Sort by distance
    result.sort(key=lambda x: x["distance_km"])

    # Apply pagination
    return result[skip : skip + limit]


def full_text_search_organizations(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 100,
) -> List[Organization]:
    """
    Perform full-text search on organizations.
    """
    search_query = db.query(Organization).filter(
        func.lower(Organization.name).contains(func.lower(query))
        | func.lower(Organization.description).contains(func.lower(query))
    )

    return search_query.offset(skip).limit(limit).all()


def full_text_search_users(
    db: Session,
    query: str,
    role: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[User]:
    """
    Perform full-text search on users.
    """
    search_query = db.query(User).filter(
        func.lower(User.full_name).contains(func.lower(query))
        | func.lower(User.email).contains(func.lower(query))
    )

    if role:
        search_query = search_query.join(User.roles).filter(User.roles.any(role=role))

    return search_query.offset(skip).limit(limit).all()


def combined_search(
    db: Session,
    query: str,
    search_type: str = "all",  # "all", "events", "resources", "organizations", "users"
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius: Optional[float] = None,
    skip: int = 0,
    limit: int = 20,
) -> Dict[str, List]:
    """
    Combined search across different entity types.
    """
    results = {}

    # Determine what to search for
    search_events = search_type in ["all", "events"]
    search_resources = search_type in ["all", "resources"]
    search_organizations = search_type in ["all", "organizations"]
    search_users = search_type in ["all", "users"]

    # Set limits based on what's being searched
    if search_type == "all":
        # If searching everything, divide the limit
        entity_limit = max(5, limit // 4)
    else:
        entity_limit = limit

    # Search resources
    if search_resources:
        resources = full_text_search_resources(db, query, skip=skip, limit=entity_limit)
        results["resources"] = resources

    # Search organizations
    if search_organizations:
        organizations = full_text_search_organizations(
            db, query, skip=skip, limit=entity_limit
        )
        results["organizations"] = organizations

    # Search users
    if search_users:
        users = full_text_search_users(db, query, skip=skip, limit=entity_limit)
        results["users"] = users

    # Search events - use geospatial if coordinates provided
    if search_events:
        if latitude is not None and longitude is not None and radius is not None:
            # Geospatial search for events
            events = geospatial_search_events(
                db, latitude, longitude, radius, skip=skip, limit=entity_limit
            )
            results["events"] = events
        else:
            # Full-text search for events - only search in title field
            events_query = (
                db.query(Event)
                .filter(func.lower(Event.title).contains(func.lower(query)))
                .offset(skip)
                .limit(entity_limit)
                .all()
            )
            results["events"] = events_query

    return results
