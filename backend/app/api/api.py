from fastapi import APIRouter

from .v1 import users_router

api_router = APIRouter()

# api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
# api_router.include_router(events_router, prefix="/events", tags=["events"])
# api_router.include_router(resources_router, prefix="/resources", tags=["resources"])
