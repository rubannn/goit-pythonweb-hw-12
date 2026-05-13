"""Pydantic schemas for authentication and password reset flows."""

from pydantic import BaseModel, EmailStr, Field


class TokenModel(BaseModel):
    """JWT access token response payload."""
    access_token: str
    token_type: str = "bearer"


class PasswordResetRequest(BaseModel):
    """Payload used to request a password reset email."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Payload used to confirm a password reset with a token."""
    token: str
    new_password: str = Field(min_length=6, max_length=128)
