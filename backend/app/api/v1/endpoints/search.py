from fastapi import APIRouter, Depends, Query
from typing import Optional, Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import get_db
from app.db.models import Event  # Add this import
from app.services import search_service
from app.api.v1.dependencies import get_current_user, get_optional_user

router = APIRouter()


@router.get("/resources")
def search_resources(
    q: str = Query(..., description="Search query string"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    organization_id: Optional[int] = Query(
        None, description="Filter by organization ID"
    ),
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(100, description="Maximum number of items to return"),
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_user),
):
    """
    Search for resources using full-text search.
    """
    resources = search_service.full_text_search_resources(
        db=db,
        query=q,
        resource_type=resource_type,
        organization_id=organization_id,
        skip=skip,
        limit=limit,
    )

    return resources


@router.get("/events")
def search_events(
    q: Optional[str] = Query(None, description="Search query string"),
    latitude: Optional[float] = Query(
        None, description="Latitude coordinate for geospatial search"
    ),
    longitude: Optional[float] = Query(
        None, description="Longitude coordinate for geospatial search"
    ),
    radius: Optional[float] = Query(10.0, description="Search radius in kilometers"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    start_date: Optional[str] = Query(
        None, description="Filter by start date (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(
        None, description="Filter by end date (YYYY-MM-DD)"
    ),
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(100, description="Maximum number of items to return"),
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_user),
):
    """
    Search for events.
    If coordinates are provided, performs geospatial search.
    Otherwise, performs full-text search.
    """
    # Determine if we should do geospatial search
    if latitude is not None and longitude is not None:
        events = search_service.geospatial_search_events(
            db=db,
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit,
        )
    elif q:
        # Fall back to regular text search if no coordinates but query provided
        events_query = db.query(Event).filter(
            func.lower(Event.title).contains(func.lower(q))
            | func.lower(Event.description).contains(func.lower(q))
        )

        if event_type:
            events_query = events_query.filter(Event.event_type == event_type)

        if start_date:
            events_query = events_query.filter(Event.start_time >= start_date)

        if end_date:
            events_query = events_query.filter(Event.end_time <= end_date)

        events = events_query.offset(skip).limit(limit).all()
    else:
        # If no query and no coordinates, return empty list
        events = []

    return events


@router.get("/organizations")
def search_organizations(
    q: str = Query(..., description="Search query string"),
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(100, description="Maximum number of items to return"),
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_user),
):
    """
    Search for organizations using full-text search.
    """
    organizations = search_service.full_text_search_organizations(
        db=db,
        query=q,
        skip=skip,
        limit=limit,
    )

    return organizations


@router.get("/users")
def search_users(
    q: str = Query(..., description="Search query string"),
    role: Optional[str] = Query(None, description="Filter by user role"),
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(100, description="Maximum number of items to return"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Search for users using full-text search.
    Requires authentication.
    """
    users = search_service.full_text_search_users(
        db=db,
        query=q,
        role=role,
        skip=skip,
        limit=limit,
    )

    return users


@router.get("/combined")
def combined_search(
    q: str = Query(..., description="Search query string"),
    search_type: str = Query(
        "all",
        description="Type of entities to search for: 'all', 'events', 'resources', 'organizations', or 'users'",
    ),
    latitude: Optional[float] = Query(
        None, description="Latitude coordinate for geospatial search"
    ),
    longitude: Optional[float] = Query(
        None, description="Longitude coordinate for geospatial search"
    ),
    radius: Optional[float] = Query(
        10.0, description="Search radius in kilometers for geospatial search"
    ),
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(
        20, description="Maximum number of items to return per entity type"
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_user),
):
    """
    Perform combined search across different entity types.
    If coordinates are provided, performs geospatial search for events.
    """
    # For users search, require authentication
    if search_type in ["all", "users"] and not current_user:
        search_type = (
            "events,resources,organizations"  # Exclude users if not authenticated
        )

    results = search_service.combined_search(
        db=db,
        query=q,
        search_type=search_type,
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        skip=skip,
        limit=limit,
    )

    return results
