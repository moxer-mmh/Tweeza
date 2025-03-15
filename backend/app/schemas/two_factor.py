from pydantic import BaseModel


class TwoFactorSetup(BaseModel):
    """Schema for 2FA setup response."""

    secret: str
    qr_code: str


class TwoFactorVerify(BaseModel):
    """Schema for 2FA verification."""

    code: str
