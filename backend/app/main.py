import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import api_router
from app.core.config import settings
from app.db.session import DatabaseConnection


# Define the initialize_db function
def initialize_db():
    """Initialize database tables and connections."""
    db_conn = DatabaseConnection()
    db_conn.create_tables()
    print("Database initialized successfully")


# Initialize app
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events
    """
    # Startup actions
    if hasattr(settings, "INITIALIZE_DB") and settings.INITIALIZE_DB:
        initialize_db()

    yield

    # Shutdown actions
    # Any cleanup code would go here


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Tweeza API",
    version="0.1.0",
    openapi_url=f"{settings.API_STR}/openapi.json",
    docs_url=f"{settings.API_STR}/docs",
    redoc_url=f"{settings.API_STR}/redoc",
    lifespan=lifespan,
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # If no specific origins, allow all
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API router
app.include_router(api_router, prefix=settings.API_STR)


@app.get("/")
async def root():
    """Root endpoint with welcome message."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs": f"{settings.API_STR}/docs",
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
