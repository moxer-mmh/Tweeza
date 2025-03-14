from fastapi import APIRouter
from .endpoints import users, auth, organizations, events, resources

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    organizations.router, prefix="/organizations", tags=["organizations"]
)
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(resources.router, prefix="/resources", tags=["resources"])
