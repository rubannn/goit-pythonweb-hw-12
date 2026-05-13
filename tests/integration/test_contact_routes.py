from datetime import date, timedelta

import pytest


@pytest.mark.asyncio
async def test_create_and_list_contacts(client, verified_user, token_factory):
    headers = {"Authorization": f"Bearer {token_factory(verified_user)}"}

    create_response = await client.post(
        "/api/contacts/",
        headers=headers,
        json={
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice@example.com",
            "phone": "+1234567891",
            "birthday": "1995-04-01",
            "additional_data": "Colleague",
        },
    )
    list_response = await client.get("/api/contacts/", headers=headers)

    assert create_response.status_code == 201
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


@pytest.mark.asyncio
async def test_search_contacts_by_first_name(
    client,
    verified_user,
    token_factory,
    contact_factory,
):
    await contact_factory(
        owner_id=verified_user.id,
        first_name="Alice",
        email="alice@example.com",
    )
    await contact_factory(
        owner_id=verified_user.id,
        first_name="Bob",
        email="bob@example.com",
    )

    response = await client.get(
        "/api/contacts/",
        headers={"Authorization": f"Bearer {token_factory(verified_user)}"},
        params={"first_name": "Ali"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["email"] == "alice@example.com"


@pytest.mark.asyncio
async def test_get_update_and_delete_contact(
    client,
    verified_user,
    token_factory,
    contact_factory,
):
    contact = await contact_factory(
        owner_id=verified_user.id,
        email="contact@example.com",
    )
    headers = {"Authorization": f"Bearer {token_factory(verified_user)}"}

    get_response = await client.get(f"/api/contacts/{contact.id}", headers=headers)
    update_response = await client.put(
        f"/api/contacts/{contact.id}",
        headers=headers,
        json={"first_name": "Updated"},
    )
    delete_response = await client.delete(f"/api/contacts/{contact.id}", headers=headers)

    assert get_response.status_code == 200
    assert update_response.status_code == 200
    assert update_response.json()["first_name"] == "Updated"
    assert delete_response.status_code == 200


@pytest.mark.asyncio
async def test_contact_routes_return_404_for_foreign_contact(
    client,
    verified_user,
    user_factory,
    token_factory,
    contact_factory,
):
    other_user = await user_factory(
        username="other-owner",
        email="other-owner@example.com",
    )
    contact = await contact_factory(
        owner_id=other_user.id,
        email="foreign@example.com",
    )

    response = await client.get(
        f"/api/contacts/{contact.id}",
        headers={"Authorization": f"Bearer {token_factory(verified_user)}"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_upcoming_birthdays_route(
    client,
    verified_user,
    token_factory,
    contact_factory,
):
    today = date.today()
    soon = today + timedelta(days=2)

    await contact_factory(
        owner_id=verified_user.id,
        email="soon@example.com",
        birthday=date(1990, soon.month, soon.day),
    )

    response = await client.get(
        "/api/contacts/upcoming-birthdays",
        headers={"Authorization": f"Bearer {token_factory(verified_user)}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["email"] == "soon@example.com"
