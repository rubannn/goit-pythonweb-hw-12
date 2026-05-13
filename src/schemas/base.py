"""Shared response schemas."""

from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Simple message envelope returned by informational endpoints."""
    message: str
