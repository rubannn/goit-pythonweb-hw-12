"""Database access helpers for contact records."""

from datetime import date, timedelta
from typing import cast

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.contact import Contact
from src.models.user import User
from src.schemas.contact import ContactCreate, ContactUpdate


def _get_next_birthday_date(birthday: date, current_date: date) -> date:
    """Calculate the next calendar occurrence of a contact's birthday."""
    try:
        next_birthday = birthday.replace(year=current_date.year)
    except ValueError:
        next_birthday = date(current_date.year, 2, 28)

    if next_birthday < current_date:
        try:
            next_birthday = birthday.replace(year=current_date.year + 1)
        except ValueError:
            next_birthday = date(current_date.year + 1, 2, 28)

    return next_birthday


async def create_contact(
    db: AsyncSession,
    body: ContactCreate,
    owner: User,
) -> Contact:
    """Create and persist a new contact for the provided owner."""
    contact = Contact(**body.model_dump(), owner_id=owner.id)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def get_contacts(db: AsyncSession, owner: User) -> list[Contact]:
    """Return all contacts belonging to the provided owner."""
    result = await db.execute(select(Contact).where(Contact.owner_id == owner.id))
    return list(result.scalars().all())


async def search_contacts(
    db: AsyncSession,
    owner: User,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
) -> list[Contact]:
    """Search owner contacts by partial first name, last name, or email."""
    filters = []
    if first_name:
        filters.append(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        filters.append(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        filters.append(Contact.email.ilike(f"%{email}%"))

    query = select(Contact).where(Contact.owner_id == owner.id)
    if filters:
        query = query.where(or_(*filters))

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_contact_by_id(
    db: AsyncSession,
    contact_id: int,
    owner: User,
) -> Contact | None:
    """Return one owner contact by identifier or ``None`` if missing."""
    result = await db.execute(
        select(Contact).where(
            Contact.id == contact_id,
            Contact.owner_id == owner.id,
        )
    )
    return result.scalar_one_or_none()


async def update_contact(
    db: AsyncSession,
    contact_id: int,
    body: ContactUpdate,
    owner: User,
) -> Contact | None:
    """Update selected contact fields for an owner-scoped record."""
    contact = await get_contact_by_id(db, contact_id, owner)

    if contact is None:
        return None

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)

    await db.commit()
    await db.refresh(contact)
    return contact


async def delete_contact(
    db: AsyncSession,
    contact_id: int,
    owner: User,
) -> Contact | None:
    """Delete an owner-scoped contact and return the deleted entity."""
    contact = await get_contact_by_id(db, contact_id, owner)

    if contact is None:
        return None

    await db.delete(contact)
    await db.commit()
    return contact


async def get_upcoming_birthdays(
    db: AsyncSession,
    owner: User,
    days: int = 7,
) -> list[Contact]:
    """Return owner contacts with birthdays occurring within the next ``days``."""
    today = date.today()
    end_date = today + timedelta(days=days)
    result = await db.execute(select(Contact).where(Contact.owner_id == owner.id))
    contacts = result.scalars().all()
    upcoming_contacts = []

    for contact in contacts:
        birthday_value = cast(date, contact.birthday)
        next_birthday = _get_next_birthday_date(birthday_value, today)

        if today <= next_birthday <= end_date:
            upcoming_contacts.append(contact)

    return upcoming_contacts
