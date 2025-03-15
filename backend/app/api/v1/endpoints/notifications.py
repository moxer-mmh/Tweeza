from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import get_db
from app.db.models import User
from app.api.v1.dependencies import get_current_user
from app.services import notification_service
from app.schemas.notification import (
    NotificationResponse,
)  # Use Pydantic schema instead of DB model

router = APIRouter()


@router.get(
    "/", response_model=List[NotificationResponse]
)  # Changed from Notification to NotificationResponse
async def read_notifications(
    skip: int = Query(0, description="Number of notifications to skip"),
    limit: int = Query(50, description="Maximum number of notifications to return"),
    unread_only: bool = Query(
        False, description="Filter to show only unread notifications"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get notifications for the current user.
    """
    notifications = notification_service.get_user_notifications(
        db, current_user.id, skip, limit, unread_only
    )
    return notifications


@router.put("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark a notification as read.
    """
    success = notification_service.mark_notification_as_read(
        db, notification_id, current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return {"success": True}


@router.get("/unread/count")
def get_unread_notification_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get count of unread notifications.
    """
    count = notification_service.get_unread_notification_count(db, current_user.id)
    return {"count": count}


@router.put("/read-all")
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark all notifications as read.
    """
    count = notification_service.mark_all_notifications_as_read(db, current_user.id)
    return {"success": True}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a notification.
    """
    success = notification_service.delete_notification(
        db, notification_id, current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return {"success": True}
