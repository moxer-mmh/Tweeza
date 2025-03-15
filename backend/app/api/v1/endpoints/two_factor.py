from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.v1.dependencies import get_current_user
from app.db import get_db, User
from app.schemas import TwoFactorSetup, TwoFactorVerify
from app.services import two_factor_service

router = APIRouter()


@router.post("/setup", response_model=TwoFactorSetup)
def setup_2fa(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Set up two-factor authentication for current user.
    Returns a secret key and QR code.
    """
    try:
        secret, qr_code = two_factor_service.setup_2fa(db, current_user.id)
        return TwoFactorSetup(secret=secret, qr_code=qr_code)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set up 2FA: {str(e)}",
        )


@router.post("/verify")
def verify_2fa_setup(
    verification: TwoFactorVerify,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Verify and enable two-factor authentication after setup.
    """
    if two_factor_service.verify_2fa_setup(db, current_user.id, verification.code):
        return {"message": "Two-factor authentication enabled successfully"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code"
    )


@router.delete("/disable")
def disable_2fa(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Disable two-factor authentication.
    """
    if two_factor_service.disable_2fa(db, current_user.id):
        return {"message": "Two-factor authentication disabled successfully"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Failed to disable two-factor authentication",
    )


@router.post("/verify-code")
def verify_code(
    verification: TwoFactorVerify,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Verify a two-factor authentication code (for testing).
    """
    if two_factor_service.verify_2fa_code(db, current_user.id, verification.code):
        return {"message": "Code is valid"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code")
