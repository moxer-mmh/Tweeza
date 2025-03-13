from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.db import Notification, User, Event, Volunteer


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def create_notification(
        self,
        user_id: int,
        title: str,
        content: str,
        notification_type: str,
        related_event_id: Optional[int] = None,
    ) -> Notification:
        """Create a new notification for a user."""
        notification = Notification(
            user_id=user_id,
            title=title,
            content=content,
            notification_type=notification_type,
            is_read=False,
            related_event_id=related_event_id,
        )

        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_user_notifications(
        self, user_id: int, skip: int = 0, limit: int = 20, unread_only: bool = False
    ) -> List[Notification]:
        """Get notifications for a user."""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)

        if unread_only:
            query = query.filter(Notification.is_read == False)

        return (
            query.order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def mark_as_read(
        self, notification_id: int, user_id: int
    ) -> Optional[Notification]:
        """Mark notification as read (with user_id validation)."""
        notification = (
            self.db.query(Notification)
            .filter(
                Notification.id == notification_id,
                Notification.user_id
                == user_id,  # Security: ensure user owns this notification
            )
            .first()
        )

        if not notification:
            return None

        notification.is_read = True
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user. Returns count updated."""
        result = (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)
            .update({"is_read": True})
        )

        self.db.commit()
        return result

    def notify_event_participants(self, event_id: int, title: str, content: str) -> int:
        """Send notification to all participants of an event. Returns count notified."""
        # Get event with participants
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise ValueError("Event not found")

        # Get all participant user IDs
        participant_volunteers = [p.volunteer_id for p in event.participants]
        participant_users = (
            self.db.query(Volunteer.user_id)
            .filter(Volunteer.id.in_(participant_volunteers))
            .all()
        )

        user_ids = [u.user_id for u in participant_users]
        count = 0

        # Create notification for each user
        for user_id in user_ids:
            self.create_notification(
                user_id=user_id,
                title=title,
                content=content,
                notification_type="event_update",
                related_event_id=event_id,
            )
            count += 1

        return count
