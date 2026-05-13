from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select

from src.models.user import User
from src.services.auth import verify_password
from src.services.email import create_email_token, create_password_reset_token


@pytest.mark.asyncio
async def test_register_user(client, monkeypatch):
    send_verification_email = AsyncMock()
    monkeypatch.setattr("src.api.auth.send_verification_email", send_verification_email)

    response = await client.post(
        "/api/auth/register",
        json={
            "username": "registered-user",
            "email": "registered@example.com",
            "password": "secret123",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "registered@example.com"
    send_verification_email.assert_awaited_once()


@pytest.mark.asyncio
async def test_login_returns_access_token(client, verified_user):
    response = await client.post(
        "/api/auth/login",
        json={"email": verified_user.email, "password": "secret123"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_verify_email_marks_user_as_verified(
    client,
    session_maker,
    user_factory,
):
    user = await user_factory(
        username="needs-verification",
        email="needs-verification@example.com",
        is_verified=False,
    )
    token = create_email_token(user.email)

    response = await client.get(f"/api/auth/verify-email/{token}")

    assert response.status_code == 200
    async with session_maker() as session:
        result = await session.execute(select(User).where(User.id == user.id))
        refreshed_user = result.scalar_one()
        assert refreshed_user.is_verified is True


@pytest.mark.asyncio
async def test_request_email_verification_resends_email(client, user_factory, monkeypatch):
    user = await user_factory(
        username="resend-user",
        email="resend@example.com",
        is_verified=False,
    )
    send_verification_email = AsyncMock()
    monkeypatch.setattr("src.api.auth.send_verification_email", send_verification_email)

    response = await client.post(
        "/api/auth/request-email",
        json={"email": user.email},
    )

    assert response.status_code == 200
    send_verification_email.assert_awaited_once_with(user.email, user.username)


@pytest.mark.asyncio
async def test_request_password_reset_is_neutral_for_unknown_email(client, monkeypatch):
    send_password_reset_email = AsyncMock()
    monkeypatch.setattr("src.api.auth.send_password_reset_email", send_password_reset_email)

    response = await client.post(
        "/api/auth/request-password-reset",
        json={"email": "missing@example.com"},
    )

    assert response.status_code == 200
    assert "If an account with this email exists" in response.json()["message"]
    send_password_reset_email.assert_not_awaited()


@pytest.mark.asyncio
async def test_reset_password_updates_password_hash(
    client,
    session_maker,
    verified_user,
):
    token = create_password_reset_token(verified_user.email)

    response = await client.post(
        "/api/auth/reset-password",
        json={"token": token, "new_password": "brandnew123"},
    )

    assert response.status_code == 200
    async with session_maker() as session:
        result = await session.execute(select(User).where(User.id == verified_user.id))
        refreshed_user = result.scalar_one()
        assert verify_password("brandnew123", refreshed_user.hashed_password)


@pytest.mark.asyncio
async def test_reset_password_rejects_invalid_token(client):
    response = await client.post(
        "/api/auth/reset-password",
        json={"token": "invalid-token", "new_password": "brandnew123"},
    )

    assert response.status_code == 400
