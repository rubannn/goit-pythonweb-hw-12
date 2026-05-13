from datetime import date, timedelta

import pytest

from src.crud.contacts import (
    create_contact,
    delete_contact,
    get_contact_by_id,
    get_contacts,
    get_upcoming_birthdays,
    search_contacts,
    update_contact,
)
from src.schemas.contact import ContactCreate, ContactUpdate


@pytest.mark.asyncio
async def test_create_and_get_contacts(db_session, verified_user):
    contact = await create_contact(
        db_session,
        ContactCreate(
            first_name="Alice",
            last_name="Smith",
            email="alice@example.com",
            phone="+1234567891",
            birthday=date(1995, 4, 1),
            additional_data="Colleague",
        ),
        verified_user,
    )

    contacts = await get_contacts(db_session, verified_user)

    assert contact.id is not None
    assert len(contacts) == 1
    assert contacts[0].email == "alice@example.com"


@pytest.mark.asyncio
async def test_search_contacts_filters_by_partial_fields(
    db_session,
    verified_user,
    contact_factory,
):
    await contact_factory(
        owner_id=verified_user.id,
        first_name="Alice",
        last_name="Smith",
        email="alice@example.com",
    )
    await contact_factory(
        owner_id=verified_user.id,
        first_name="Bob",
        last_name="Johnson",
        email="bob@example.com",
    )

    results = await search_contacts(db_session, verified_user, first_name="Ali")

    assert len(results) == 1
    assert results[0].email == "alice@example.com"


@pytest.mark.asyncio
async def test_get_contact_by_id_respects_owner_scope(
    db_session,
    verified_user,
    user_factory,
    contact_factory,
):
    other_user = await user_factory(
        username="other-user",
        email="other@example.com",
    )
    contact = await contact_factory(
        owner_id=other_user.id,
        email="private@example.com",
    )

    found_contact = await get_contact_by_id(db_session, contact.id, verified_user)

    assert found_contact is None


@pytest.mark.asyncio
async def test_update_contact_changes_selected_fields(
    db_session,
    verified_user,
    contact_factory,
):
    contact = await contact_factory(
        owner_id=verified_user.id,
        email="before@example.com",
        first_name="Before",
    )

    updated_contact = await update_contact(
        db_session,
        contact.id,
        ContactUpdate(first_name="After", email="after@example.com"),
        verified_user,
    )

    assert updated_contact is not None
    assert updated_contact.first_name == "After"
    assert updated_contact.email == "after@example.com"


@pytest.mark.asyncio
async def test_delete_contact_removes_record(
    db_session,
    verified_user,
    contact_factory,
):
    contact = await contact_factory(
        owner_id=verified_user.id,
        email="delete@example.com",
    )

    deleted_contact = await delete_contact(db_session, contact.id, verified_user)
    remaining_contacts = await get_contacts(db_session, verified_user)

    assert deleted_contact is not None
    assert remaining_contacts == []


@pytest.mark.asyncio
async def test_get_upcoming_birthdays_returns_contacts_within_window(
    db_session,
    verified_user,
    contact_factory,
):
    today = date.today()
    in_three_days = today + timedelta(days=3)
    in_ten_days = today + timedelta(days=10)

    await contact_factory(
        owner_id=verified_user.id,
        email="soon@example.com",
        birthday=date(1990, in_three_days.month, in_three_days.day),
    )
    await contact_factory(
        owner_id=verified_user.id,
        email="later@example.com",
        birthday=date(1990, in_ten_days.month, in_ten_days.day),
    )

    results = await get_upcoming_birthdays(db_session, verified_user, days=7)

    assert len(results) == 1
    assert results[0].email == "soon@example.com"
