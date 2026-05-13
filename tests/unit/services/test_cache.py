import json

import pytest

from src.models.user import User
from src.services import cache as cache_service


@pytest.mark.asyncio
async def test_set_and_get_cached_user(fake_redis):
    user = User(
        id=1,
        username="cached-user",
        email="cached@example.com",
        hashed_password="hash",
        role="user",
        is_verified=True,
    )

    await cache_service.set_cached_user(user)
    cached_user = await cache_service.get_cached_user(user.email)

    assert cached_user is not None
    assert cached_user.email == user.email


@pytest.mark.asyncio
async def test_get_cached_user_returns_none_for_invalid_json(fake_redis):
    await fake_redis.set("user:broken@example.com", "{not-json}")

    cached_user = await cache_service.get_cached_user("broken@example.com")

    assert cached_user is None


@pytest.mark.asyncio
async def test_invalidate_user_cache_removes_entry(fake_redis):
    await fake_redis.set(
        "user:cached@example.com",
        json.dumps({"id": 1, "username": "cached", "email": "cached@example.com", "hashed_password": "hash", "role": "user", "is_verified": True}),
    )

    await cache_service.invalidate_user_cache("cached@example.com")

    assert await fake_redis.get("user:cached@example.com") is None
