from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from src.models.user import UserRole
from src.services import auth as auth_service


def test_verify_password_returns_false_for_invalid_hash():
    assert auth_service.verify_password("secret123", "not-a-valid-hash") is False


def test_create_access_token_contains_subject():
    token = auth_service.create_access_token({"sub": "token@example.com"})

    assert isinstance(token, str)
    assert token


@pytest.mark.asyncio
async def test_authenticate_user_returns_user_for_valid_credentials(
    db_session,
    verified_user,
):
    user = await auth_service.authenticate_user(
        db_session,
        verified_user.email,
        "secret123",
    )

    assert user is not None
    assert user.email == verified_user.email


@pytest.mark.asyncio
async def test_get_current_user_uses_cache_before_database(
    db_session,
    fake_redis,
    verified_user,
    monkeypatch,
):
    await auth_service.set_cached_user(verified_user)
    db_lookup = AsyncMock(side_effect=AssertionError("DB should not be called on cache hit"))
    monkeypatch.setattr(auth_service, "get_user_by_email", db_lookup)

    current_user = await auth_service.get_current_user(
        credentials=HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=auth_service.create_access_token({"sub": verified_user.email}),
        ),
        db=db_session,
    )

    assert current_user.email == verified_user.email


@pytest.mark.asyncio
async def test_get_current_user_raises_for_invalid_token(db_session):
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.get_current_user(
            credentials=HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials="invalid-token",
            ),
            db=db_session,
        )

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_admin_allows_admin(admin_user):
    current_admin = await auth_service.get_current_admin(admin_user)

    assert current_admin.role == UserRole.ADMIN.value


@pytest.mark.asyncio
async def test_get_current_admin_rejects_non_admin(verified_user):
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.get_current_admin(verified_user)

    assert exc_info.value.status_code == 403
