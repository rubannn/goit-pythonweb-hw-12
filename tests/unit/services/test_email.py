import pytest

from src.services import email as email_service


def test_email_verification_token_roundtrip():
    token = email_service.create_email_token("verify@example.com")

    decoded_email = email_service.get_email_from_token(token)

    assert decoded_email == "verify@example.com"


def test_invalid_verification_token_raises_value_error():
    with pytest.raises(ValueError, match="Invalid verification token"):
        email_service.get_email_from_token("bad-token")


def test_password_reset_token_roundtrip():
    token = email_service.create_password_reset_token("reset@example.com")

    decoded_email = email_service.get_email_from_password_reset_token(token)

    assert decoded_email == "reset@example.com"


def test_invalid_password_reset_token_raises_value_error():
    with pytest.raises(ValueError, match="Invalid password reset token"):
        email_service.get_email_from_password_reset_token("bad-token")


@pytest.mark.asyncio
async def test_send_verification_email_logs_link_when_suppressed(capsys):
    await email_service.send_verification_email("verify@example.com", "verify-user")

    captured = capsys.readouterr()

    assert "Verification link" in captured.out
    assert "verify@example.com" in captured.out


@pytest.mark.asyncio
async def test_send_password_reset_email_logs_link_when_suppressed(capsys):
    await email_service.send_password_reset_email("reset@example.com", "reset-user")

    captured = capsys.readouterr()

    assert "Password reset link" in captured.out
    assert "reset@example.com" in captured.out
