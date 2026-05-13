"""Pydantic schemas for contact requests and responses."""

from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactBase(BaseModel):
    """Shared contact fields used across request and response schemas."""
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    phone: str = Field(min_length=5, max_length=20)
    birthday: date
    additional_data: str | None = None


class ContactCreate(ContactBase):
    """Payload used to create a new contact."""
    pass


class ContactUpdate(BaseModel):
    """Partial payload used to update an existing contact."""
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=5, max_length=20)
    birthday: date | None = None
    additional_data: str | None = None


class ContactResponse(ContactBase):
    """Public representation of a contact returned by the API."""
    id: int
    owner_id: int | None = None

    model_config = ConfigDict(from_attributes=True)
