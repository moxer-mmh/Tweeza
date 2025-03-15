from fastapi import APIRouter
from .endpoints import (
    users,
    auth,
    organizations,
    events,
    resources,
    search,
    two_factor,
    notifications,
    analytics,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    organizations.router, prefix="/organizations", tags=["organizations"]
)
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(resources.router, prefix="/resources", tags=["resources"])
api_router.include_router(two_factor.router, prefix="/2fa", tags=["two-factor"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(
    notifications.router, prefix="/notifications", tags=["notifications"]
)
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
