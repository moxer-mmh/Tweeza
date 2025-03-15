import pytest
from unittest.mock import patch
from fastapi import status


@pytest.fixture
def two_factor_setup_data():
    """Data for setting up 2FA."""
    return {"method": "sms", "phone_number": "+1234567890"}


def test_enable_two_factor(client, token_headers, two_factor_setup_data):
    """Test enabling two-factor authentication."""
    with patch(
        "app.api.v1.endpoints.two_factor.two_factor_service.enable_two_factor"
    ) as mock_enable:
        mock_enable.return_value = True

        response = client.post(
            "/api/v1/auth/two-factor/enable",
            json=two_factor_setup_data,
            headers=token_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True


def test_disable_two_factor(client, token_headers):
    """Test disabling two-factor authentication."""
    with patch(
        "app.api.v1.endpoints.two_factor.two_factor_service.disable_two_factor"
    ) as mock_disable:
        mock_disable.return_value = True

        response = client.post("/api/v1/auth/two-factor/disable", headers=token_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True


def test_send_verification_code(client, token_headers):
    """Test sending verification code."""
    with patch(
        "app.api.v1.endpoints.two_factor.two_factor_service.send_verification_code"
    ) as mock_send:
        mock_send.return_value = True

        response = client.post(
            "/api/v1/auth/two-factor/send-code", headers=token_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True


def test_verify_code(client, token_headers):
    """Test verifying 2FA code."""
    with patch(
        "app.api.v1.endpoints.two_factor.two_factor_service.verify_code"
    ) as mock_verify:
        mock_verify.return_value = True

        response = client.post(
            "/api/v1/auth/two-factor/verify",
            json={"code": "123456"},
            headers=token_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data


def test_get_two_factor_status(client, token_headers):
    """Test getting two-factor authentication status."""
    with patch(
        "app.api.v1.endpoints.two_factor.two_factor_service.get_user_two_factor"
    ) as mock_get:
        mock_get.return_value = {
            "is_enabled": True,
            "method": "sms",
            "phone_number": "+1234567890",
        }

        response = client.get("/api/v1/auth/two-factor/status", headers=token_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_enabled"] is True
        assert data["method"] == "sms"
