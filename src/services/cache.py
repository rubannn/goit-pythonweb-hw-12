import json
from datetime import datetime
from typing import Any

from redis import RedisError
from redis.asyncio import Redis

from src.database.config import settings
from src.models.user import User


_redis_client: Redis | None = None


def _serialize_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


def _deserialize_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value)


def _user_cache_key(email: str) -> str:
    return f"user:{email.lower()}"


def get_redis_client() -> Redis:
    global _redis_client

    if _redis_client is None:
        _redis_client = Redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )

    return _redis_client


async def close_redis_client() -> None:
    global _redis_client

    if _redis_client is None:
        return

    await _redis_client.aclose()
    _redis_client = None


def _user_to_cache_payload(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "hashed_password": user.hashed_password,
        "role": user.role,
        "is_verified": user.is_verified,
        "avatar_url": user.avatar_url,
        "created_at": _serialize_datetime(user.created_at),
        "updated_at": _serialize_datetime(user.updated_at),
    }


def _user_from_cache_payload(payload: dict[str, Any]) -> User:
    return User(
        id=payload["id"],
        username=payload["username"],
        email=payload["email"],
        hashed_password=payload["hashed_password"],
        role=payload["role"],
        is_verified=payload["is_verified"],
        avatar_url=payload.get("avatar_url"),
        created_at=_deserialize_datetime(payload.get("created_at")),
        updated_at=_deserialize_datetime(payload.get("updated_at")),
    )


async def get_cached_user(email: str) -> User | None:
    try:
        cached_value = await get_redis_client().get(_user_cache_key(email))
    except (RedisError, OSError):
        return None

    if cached_value is None:
        return None

    try:
        payload = json.loads(cached_value)
    except json.JSONDecodeError:
        return None

    return _user_from_cache_payload(payload)


async def set_cached_user(user: User) -> None:
    try:
        await get_redis_client().setex(
            _user_cache_key(user.email),
            settings.REDIS_USER_CACHE_TTL,
            json.dumps(_user_to_cache_payload(user)),
        )
    except (RedisError, OSError):
        return


async def invalidate_user_cache(email: str) -> None:
    try:
        await get_redis_client().delete(_user_cache_key(email))
    except (RedisError, OSError):
        return
