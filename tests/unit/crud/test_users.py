import pytest
from sqlalchemy import select

from src.crud.users import (
    confirm_user_email,
    create_user,
    get_user_by_email,
    update_avatar_url,
    update_user_password,
)
from src.models.user import User, UserRole
from src.schemas.user import UserCreate
from src.services.auth import get_password_hash, verify_password


@pytest.mark.asyncio
async def test_create_user_assigns_default_role(db_session):
    body = UserCreate(
        username="new-user",
        email="new-user@example.com",
        password="secret123",
    )

    user = await create_user(db_session, body, get_password_hash(body.password))

    assert user.id is not None
    assert user.role == UserRole.USER.value
    assert user.email == body.email


@pytest.mark.asyncio
async def test_get_user_by_email_returns_user(db_session):
    user = User(
        username="lookup-user",
        email="lookup@example.com",
        hashed_password=get_password_hash("secret123"),
        role=UserRole.USER.value,
        is_verified=False,
    )
    db_session.add(user)
    await db_session.commit()

    found_user = await get_user_by_email(db_session, user.email)

    assert found_user is not None
    assert found_user.email == user.email


@pytest.mark.asyncio
async def test_confirm_user_email_marks_user_as_verified(db_session):
    user = User(
        username="verify-user",
        email="verify@example.com",
        hashed_password=get_password_hash("secret123"),
        role=UserRole.USER.value,
        is_verified=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    updated_user = await confirm_user_email(db_session, user)

    assert updated_user.is_verified is True


@pytest.mark.asyncio
async def test_update_avatar_url_persists_new_value(db_session):
    user = User(
        username="avatar-user",
        email="avatar@example.com",
        hashed_password=get_password_hash("secret123"),
        role=UserRole.ADMIN.value,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    updated_user = await update_avatar_url(
        db_session,
        user,
        "https://cdn.example.com/avatar.jpg",
    )

    assert updated_user.avatar_url == "https://cdn.example.com/avatar.jpg"


@pytest.mark.asyncio
async def test_update_user_password_replaces_password_hash(db_session):
    user = User(
        username="password-user",
        email="password@example.com",
        hashed_password=get_password_hash("old-secret"),
        role=UserRole.USER.value,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    updated_user = await update_user_password(
        db_session,
        user,
        get_password_hash("new-secret"),
    )

    result = await db_session.execute(select(User).where(User.id == user.id))
    reloaded_user = result.scalar_one()

    assert updated_user.id == user.id
    assert verify_password("new-secret", reloaded_user.hashed_password)
