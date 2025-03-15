from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.db.models import User, Notification
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.schemas.notification import NotificationCreate


def create_notification(
    db: Session,
    notification_data: NotificationCreate,
) -> Notification:
    """
    Create a new in-app notification for a user.
    """
    notification = Notification(
        user_id=notification_data.recipient_id,
        title=notification_data.title,
        message=notification_data.message,
        notification_type=notification_data.type.value,
        related_id=notification_data.reference_id,
        related_type=None,  # Could be derived from type if needed
        read=False,
        created_at=datetime.now(),
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_notification(db: Session, notification_id: int) -> Optional[Notification]:
    """
    Get a specific notification by ID.
    """
    return db.query(Notification).filter(Notification.id == notification_id).first()


def get_user_notifications(
    db: Session, user_id: int, skip: int = 0, limit: int = 50, unread_only: bool = False
) -> List[Notification]:
    """
    Get notifications for a specific user.
    """
    query = db.query(Notification).filter(Notification.user_id == user_id)

    if unread_only:
        query = query.filter(Notification.read == False)

    return (
        query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    )


def get_unread_notification_count(db: Session, user_id: int) -> int:
    """
    Get count of unread notifications for a user.
    """
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.read == False)
        .count()
    )


def mark_notification_as_read(
    db: Session, notification_id: int, user_id: Optional[int] = None
) -> bool:
    """
    Mark a notification as read.
    """
    query = db.query(Notification).filter(Notification.id == notification_id)

    if user_id is not None:
        query = query.filter(Notification.user_id == user_id)

    notification = query.first()

    if not notification:
        return False

    notification.read = True
    notification.read_at = datetime.now()
    db.commit()
    return True


def mark_all_notifications_as_read(db: Session, user_id: int) -> int:
    """
    Mark all notifications as read for a user.
    Returns the number of updated notifications.
    """
    result = (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.read == False)
        .update({"read": True, "read_at": datetime.now()})
    )

    db.commit()
    return result


def delete_notification(db: Session, notification_id: int, user_id: int) -> bool:
    """
    Delete a notification.
    """
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == user_id)
        .first()
    )

    if not notification:
        return False

    db.delete(notification)
    db.commit()
    return True


def send_email(
    recipient_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
) -> bool:
    """
    Send an email to a user.
    """
    # Skip if email settings are not configured
    if not settings.EMAIL_HOST or not settings.EMAIL_PORT or not settings.EMAIL_USER:
        print("Email settings not configured, skipping email send")
        return False

    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = recipient_email

        # Add text content if provided, otherwise use a simple extraction from HTML
        if text_content is None:
            # Very simplistic HTML to text conversion
            text_content = (
                html_content.replace("<br>", "\n")
                .replace("<p>", "")
                .replace("</p>", "\n\n")
            )

        # Attach parts
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        msg.attach(part1)
        msg.attach(part2)

        # Send email
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            if settings.EMAIL_USE_TLS:
                server.starttls()

            if settings.EMAIL_USER and settings.EMAIL_PASSWORD:
                server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)

            server.sendmail(settings.EMAIL_FROM, recipient_email, msg.as_string())

        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False


def send_email_notification(
    recipient_email: str,
    subject: str,
    content: str,
) -> bool:
    """
    Send an email notification to a user.
    """
    return send_email(recipient_email, subject, content)


def notify_user_by_email(
    db: Session,
    user_id: int,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
) -> bool:
    """
    Send an email notification to a user.
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.email:
        return False

    return send_email(user.email, subject, html_content, text_content)


def send_sms(
    phone_number: str,
    message: str,
) -> bool:
    """
    Send an SMS message. This is a placeholder implementation.
    """
    # This would be replaced with actual SMS sending logic, e.g., using Twilio
    print(f"Would send SMS to {phone_number}: {message}")
    return True


def send_sms_notification(
    phone_number: str,
    message: str,
) -> bool:
    """
    Send an SMS notification.
    """
    return send_sms(phone_number, message)


# Keep existing placeholder functions
def notify_resource_contribution(db: Session, contribution_id: int) -> None:
    """
    Send notifications for a new resource contribution.
    """
    # ...existing code...
    pass


def notify_event_registration(db: Session, registration_id: int) -> None:
    """
    Send notifications for a new event registration.
    """
    # ...existing code...
    pass
