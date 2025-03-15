from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any


class OAuthProvider(str, Enum):
    GOOGLE = "google"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    GITHUB = "github"


class OAuthRequest(BaseModel):
    provider: OAuthProvider
    access_token: str


class OAuthUserInfo(BaseModel):
    provider: OAuthProvider
    provider_user_id: str
    email: EmailStr
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None
    raw_data: Dict[str, Any]
