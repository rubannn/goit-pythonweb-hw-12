"""Database engine, base model, and session helpers."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.database.config import settings


class Base(DeclarativeBase):
    """Base SQLAlchemy declarative class for all ORM models."""
    pass


engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session for a request and close it afterwards."""
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()
