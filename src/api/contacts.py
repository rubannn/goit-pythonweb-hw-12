from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.contacts import (
    create_contact,
    delete_contact,
    get_contact_by_id,
    get_contacts,
    get_upcoming_birthdays,
    search_contacts,
    update_contact,
)
from src.database.db import get_db
from src.models.contact import Contact
from src.models.user import User
from src.schemas.contact import ContactCreate, ContactResponse, ContactUpdate
from src.services.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["contacts"])


def to_contact_response(contact: Contact) -> ContactResponse:
    return ContactResponse.model_validate(contact)


def to_contact_response_list(contacts: list[Contact]) -> list[ContactResponse]:
    return [ContactResponse.model_validate(contact) for contact in contacts]


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact_endpoint(
    body: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ContactResponse:
    contact = await create_contact(db, body, current_user)
    return to_contact_response(contact)


@router.get("/", response_model=list[ContactResponse])
async def get_contacts_endpoint(
    first_name: str | None = Query(default=None),
    last_name: str | None = Query(default=None),
    email: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ContactResponse]:
    if first_name or last_name or email:
        contacts = await search_contacts(
            db,
            current_user,
            first_name,
            last_name,
            email,
        )
        return to_contact_response_list(contacts)

    contacts = await get_contacts(db, current_user)
    return to_contact_response_list(contacts)


@router.get("/upcoming-birthdays", response_model=list[ContactResponse])
async def get_upcoming_birthdays_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ContactResponse]:
    contacts = await get_upcoming_birthdays(db, current_user)
    return to_contact_response_list(contacts)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact_by_id_endpoint(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ContactResponse:
    contact = await get_contact_by_id(db, contact_id, current_user)

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    return to_contact_response(contact)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact_endpoint(
    contact_id: int,
    body: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ContactResponse:
    contact = await update_contact(db, contact_id, body, current_user)

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    return to_contact_response(contact)


@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact_endpoint(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ContactResponse:
    contact = await delete_contact(db, contact_id, current_user)

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    return to_contact_response(contact)
