"""Pydantic schemas for user-related requests and responses."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.models.user import UserRole


class UserBase(BaseModel):
    """Fields shared by user creation and response schemas."""
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Payload used to register a new user."""
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    """Credentials payload for user authentication."""
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserResponse(UserBase):
    """Public representation of a user returned by the API."""
    id: int
    role: UserRole
    is_verified: bool
    avatar_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RequestEmail(BaseModel):
    """Payload used to request a verification email resend."""
    email: EmailStr
