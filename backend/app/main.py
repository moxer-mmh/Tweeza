from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router


app = FastAPI(
    title="Tweeza API",
    description="API for the Tweeza community volunteering platform",
    version="0.1.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Welcome to Tweeza API"}
