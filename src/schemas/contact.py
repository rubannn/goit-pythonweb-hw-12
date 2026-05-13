from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    phone: str = Field(min_length=5, max_length=20)
    birthday: date
    additional_data: str | None = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=5, max_length=20)
    birthday: date | None = None
    additional_data: str | None = None


class ContactResponse(ContactBase):
    id: int
    owner_id: int | None = None

    model_config = ConfigDict(from_attributes=True)
