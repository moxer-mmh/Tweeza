import pytest
from fastapi import status
from app.schemas import NotificationCreate, NotificationType


def test_get_user_notifications(client, token_headers):
    """Test getting user notifications."""
    response = client.get("/api/v1/notifications/", headers=token_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_mark_notification_as_read(client, token_headers, db_session):
    """Test marking a notification as read."""
    # First create a notification for the user
    from app.services.notification_service import create_notification

    notification = create_notification(
        db_session,
        NotificationCreate(
            recipient_id=1,  # Assuming user ID 1 for test user
            title="Test Notification",
            message="This is a test notification",
            type=NotificationType.EVENT_INVITE,
            reference_id=123,
        ),
    )

    # Mark as read - use PUT instead of POST
    response = client.put(
        f"/api/v1/notifications/{notification.id}/read", headers=token_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True


def test_get_unread_notification_count(client, token_headers):
    """Test getting count of unread notifications."""
    response = client.get("/api/v1/notifications/unread/count", headers=token_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "count" in data
    assert isinstance(data["count"], int)


def test_mark_all_notifications_as_read(client, token_headers):
    """Test marking all notifications as read."""
    # Use PUT instead of POST
    response = client.put("/api/v1/notifications/read-all", headers=token_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True

    # Verify unread count is now zero
    count_response = client.get(
        "/api/v1/notifications/unread/count", headers=token_headers
    )
    assert count_response.json()["count"] == 0


def test_delete_notification(client, token_headers, db_session):
    """Test deleting a notification."""
    # First create a notification for the user
    from app.services.notification_service import create_notification

    notification = create_notification(
        db_session,
        NotificationCreate(
            recipient_id=1,  # Assuming user ID 1 for test user
            title="Test Notification for Deletion",
            message="This notification will be deleted",
            type=NotificationType.EVENT_INVITE,
            reference_id=123,
        ),
    )

    # Delete notification
    response = client.delete(
        f"/api/v1/notifications/{notification.id}", headers=token_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
