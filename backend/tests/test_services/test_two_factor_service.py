import pytest
from unittest.mock import patch, MagicMock
from app.services import two_factor_service
from app.db.models import User


@pytest.fixture
def test_user_with_2fa(db_session, test_user):
    """Create a test user with 2FA enabled."""
    # Set 2FA fields directly on the user model
    test_user.two_factor_secret = "TESTSECRET123456"
    test_user.two_factor_enabled = True
    db_session.commit()
    db_session.refresh(test_user)
    return test_user


def test_generate_totp_secret():
    """Test generating a TOTP secret."""
    with patch("pyotp.random_base32", return_value="TESTSECRET123456"):
        secret = two_factor_service.generate_totp_secret()
        assert secret == "TESTSECRET123456"


def test_get_totp_qr_code():
    """Test generating a QR code for TOTP setup."""
    with patch("pyotp.TOTP") as mock_totp:
        mock_totp_instance = MagicMock()
        mock_totp_instance.provisioning_uri.return_value = (
            "otpauth://totp/Test:user@example.com?secret=TESTSECRET123456&issuer=Test"
        )
        mock_totp.return_value = mock_totp_instance

        with patch("qrcode.QRCode") as mock_qr:
            mock_qr_instance = MagicMock()
            mock_qr.return_value = mock_qr_instance

            with patch("io.BytesIO") as mock_bytesio:
                with patch("base64.b64encode") as mock_b64encode:
                    mock_b64encode.return_value.decode.return_value = "QRCODE_DATA"

                    qr_code = two_factor_service.get_totp_qr_code(
                        "user@example.com", "TESTSECRET123456"
                    )

                    assert qr_code == "data:image/png;base64,QRCODE_DATA"
                    mock_totp_instance.provisioning_uri.assert_called_once_with(
                        name="user@example.com", issuer_name="Tweeza"
                    )


def test_setup_2fa(db_session, test_user):
    """Test setting up 2FA for a user."""
    with patch(
        "app.services.two_factor_service.generate_totp_secret",
        return_value="TESTSECRET123456",
    ):
        with patch(
            "app.services.two_factor_service.get_totp_qr_code",
            return_value="data:image/png;base64,QRCODE_DATA",
        ):
            secret, qr_code = two_factor_service.setup_2fa(db_session, test_user.id)

            assert secret == "TESTSECRET123456"
            assert qr_code == "data:image/png;base64,QRCODE_DATA"

            # Check that the secret was stored on the user
            db_session.refresh(test_user)
            assert test_user.two_factor_secret == "TESTSECRET123456"
            assert (
                test_user.two_factor_enabled is None
                or test_user.two_factor_enabled is False
            )


def test_verify_2fa_setup(db_session, test_user):
    """Test verifying 2FA setup with a code."""
    # First set up 2FA
    test_user.two_factor_secret = "TESTSECRET123456"
    db_session.commit()

    with patch("pyotp.TOTP") as mock_totp:
        mock_totp_instance = MagicMock()
        mock_totp_instance.verify.return_value = True
        mock_totp.return_value = mock_totp_instance

        result = two_factor_service.verify_2fa_setup(db_session, test_user.id, "123456")

        assert result is True
        mock_totp_instance.verify.assert_called_once_with("123456")

        # Check that 2FA was enabled
        db_session.refresh(test_user)
        assert test_user.two_factor_enabled is True


def test_disable_2fa(db_session, test_user_with_2fa):
    """Test disabling 2FA for a user."""
    result = two_factor_service.disable_2fa(db_session, test_user_with_2fa.id)

    assert result is True

    # Check that 2FA was disabled
    db_session.refresh(test_user_with_2fa)
    assert test_user_with_2fa.two_factor_enabled is False
    assert test_user_with_2fa.two_factor_secret is None


def test_verify_2fa_code(db_session, test_user_with_2fa):
    """Test verifying a 2FA code."""
    with patch("pyotp.TOTP") as mock_totp:
        mock_totp_instance = MagicMock()
        mock_totp_instance.verify.return_value = True
        mock_totp.return_value = mock_totp_instance

        result = two_factor_service.verify_2fa_code(
            db_session, test_user_with_2fa.id, "123456"
        )

        assert result is True
        mock_totp_instance.verify.assert_called_once_with("123456")


def test_verify_2fa_code_invalid_user(db_session):
    """Test verifying a 2FA code with invalid user ID."""
    result = two_factor_service.verify_2fa_code(db_session, 9999, "123456")
    assert result is False


def test_verify_2fa_code_not_enabled(db_session, test_user):
    """Test verifying a 2FA code when 2FA is not enabled."""
    result = two_factor_service.verify_2fa_code(db_session, test_user.id, "123456")
    assert result is False
