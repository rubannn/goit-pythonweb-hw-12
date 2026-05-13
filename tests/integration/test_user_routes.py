from io import BytesIO
from unittest.mock import AsyncMock

import pytest


@pytest.mark.asyncio
async def test_read_current_user_profile(client, verified_user, token_factory):
    response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token_factory(verified_user)}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == verified_user.email


@pytest.mark.asyncio
async def test_read_current_user_requires_authentication(client):
    response = await client.get("/api/users/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_avatar_requires_admin_role(client, verified_user, token_factory):
    response = await client.patch(
        "/api/users/avatar",
        headers={"Authorization": f"Bearer {token_factory(verified_user)}"},
        files={"file": ("avatar.png", BytesIO(b"fake-image"), "image/png")},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_avatar_for_admin(client, admin_user, token_factory, monkeypatch):
    upload_avatar = AsyncMock(return_value="https://cdn.example.com/admin-avatar.png")
    monkeypatch.setattr("src.api.users.upload_avatar", upload_avatar)

    response = await client.patch(
        "/api/users/avatar",
        headers={"Authorization": f"Bearer {token_factory(admin_user)}"},
        files={"file": ("avatar.png", BytesIO(b"fake-image"), "image/png")},
    )

    assert response.status_code == 200
    assert response.json()["avatar_url"] == "https://cdn.example.com/admin-avatar.png"
    upload_avatar.assert_awaited_once()
