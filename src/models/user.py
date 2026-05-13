"""User ORM model and role definitions."""

from enum import StrEnum

from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from src.database.db import Base


class UserRole(StrEnum):
    """Available application roles for authorization checks."""
    USER = "user"
    ADMIN = "admin"


class User(Base):
    """Persisted user account entity."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default=UserRole.USER.value, server_default=UserRole.USER.value)
    is_verified = Column(Boolean, default=False, nullable=False)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    contacts = relationship("Contact", back_populates="owner", cascade="all, delete-orphan")
