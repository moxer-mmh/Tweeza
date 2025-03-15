import pytest
from unittest.mock import patch, MagicMock
from app.services import notification_service
from app.schemas import NotificationCreate, NotificationType


@pytest.fixture
def notification_data():
    """Create test notification data."""
    return {
        "recipient_id": 1,
        "title": "Test Notification",
        "message": "This is a test notification",
        "type": NotificationType.EVENT_INVITE,
        "reference_id": 123,
    }


def test_create_notification(db_session, test_user, notification_data):
    """Test creating a new notification."""
    notification_schema = NotificationCreate(**notification_data)

    notification = notification_service.create_notification(
        db_session, notification_schema
    )

    assert notification is not None
    assert notification.user_id == notification_data["recipient_id"]
    assert notification.title == notification_data["title"]
    assert notification.message == notification_data["message"]
    assert notification.notification_type == notification_data["type"].value
    assert notification.related_id == notification_data["reference_id"]
    assert notification.read is False


def test_get_user_notifications(db_session, test_user):
    """Test getting notifications for a user."""
    # First create some notifications
    for i in range(3):
        notification_service.create_notification(
            db_session,
            NotificationCreate(
                recipient_id=test_user.id,
                title=f"Test {i}",
                message=f"Message {i}",
                type=NotificationType.EVENT_INVITE,
                reference_id=i,
            ),
        )

    # Get notifications
    notifications = notification_service.get_user_notifications(
        db_session, test_user.id
    )

    # Verify
    assert len(notifications) >= 3
    assert all(n.user_id == test_user.id for n in notifications)


def test_mark_notification_as_read(db_session, test_user):
    """Test marking a notification as read."""
    # Create notification
    notification = notification_service.create_notification(
        db_session,
        NotificationCreate(
            recipient_id=test_user.id,
            title="Test Notification",
            message="This is a test notification",
            type=NotificationType.EVENT_INVITE,
            reference_id=1,
        ),
    )

    # Verify it's unread
    assert notification.read is False

    # Mark as read
    updated = notification_service.mark_notification_as_read(
        db_session, notification.id
    )

    # Verify
    assert updated is True

    # Fetch updated notification
    read_notification = notification_service.get_notification(
        db_session, notification.id
    )
    assert read_notification.read is True


@patch("app.services.notification_service.send_email")
def test_send_email_notification(mock_send_email, db_session):
    """Test sending an email notification."""
    # Test data
    recipient_email = "test@example.com"
    subject = "Test Email"
    content = "This is a test email"

    # Call function
    notification_service.send_email_notification(recipient_email, subject, content)

    # Verify email was sent
    mock_send_email.assert_called_once_with(recipient_email, subject, content)


@patch("app.services.notification_service.send_sms")
def test_send_sms_notification(mock_send_sms):
    """Test sending an SMS notification."""
    # Test data
    phone_number = "+1234567890"
    message = "This is a test SMS"

    # Call function
    notification_service.send_sms_notification(phone_number, message)

    # Verify SMS was sent
    mock_send_sms.assert_called_once_with(phone_number, message)
