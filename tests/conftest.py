from collections.abc import AsyncGenerator, Awaitable, Callable
from datetime import UTC, datetime

import fakeredis.aioredis
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import src.models  # noqa: F401
from src.database.db import Base, get_db
from src.main import app
from src.models.contact import Contact
from src.models.user import User, UserRole
from src.services import cache as cache_service
from src.services.auth import create_access_token, get_password_hash


@pytest.fixture(autouse=True)
def disable_rate_limiter() -> AsyncGenerator[None, None]:
    previous_state = app.state.limiter.enabled
    app.state.limiter.enabled = False
    try:
        yield
    finally:
        app.state.limiter.enabled = previous_state


@pytest.fixture
async def session_maker(tmp_path) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    db_path = tmp_path / "test.db"
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{db_path}",
        future=True,
    )
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    try:
        yield session_factory
    finally:
        await engine.dispose()


@pytest.fixture
async def db_session(
    session_maker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        yield session


@pytest.fixture(autouse=True)
async def fake_redis(monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[fakeredis.aioredis.FakeRedis, None]:
    redis_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(cache_service, "_redis_client", redis_client)
    monkeypatch.setattr(cache_service, "get_redis_client", lambda: redis_client)
    try:
        yield redis_client
    finally:
        await redis_client.flushall()
        await redis_client.aclose()
        cache_service._redis_client = None


@pytest.fixture
async def client(
    session_maker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client

    app.dependency_overrides.clear()


@pytest.fixture
def user_factory(
    session_maker: async_sessionmaker[AsyncSession],
) -> Callable[..., Awaitable[User]]:
    async def _create_user(
        *,
        username: str = "test-user",
        email: str = "user@example.com",
        password: str = "secret123",
        role: UserRole = UserRole.USER,
        is_verified: bool = True,
        avatar_url: str | None = None,
    ) -> User:
        async with session_maker() as session:
            user = User(
                username=username,
                email=email,
                hashed_password=get_password_hash(password),
                role=role.value,
                is_verified=is_verified,
                avatar_url=avatar_url,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    return _create_user


@pytest.fixture
def contact_factory(
    session_maker: async_sessionmaker[AsyncSession],
) -> Callable[..., Awaitable[Contact]]:
    async def _create_contact(
        *,
        owner_id: int,
        first_name: str = "John",
        last_name: str = "Doe",
        email: str = "john.doe@example.com",
        phone: str = "+1234567890",
        birthday=None,
        additional_data: str | None = "Friend",
    ) -> Contact:
        from datetime import date

        async with session_maker() as session:
            contact = Contact(
                owner_id=owner_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                birthday=birthday or date(1990, 1, 1),
                additional_data=additional_data,
            )
            session.add(contact)
            await session.commit()
            await session.refresh(contact)
            return contact

    return _create_contact


@pytest.fixture
def token_factory() -> Callable[[User], str]:
    def _create_token(user: User) -> str:
        return create_access_token({"sub": user.email})

    return _create_token


@pytest.fixture
async def verified_user(user_factory: Callable[..., Awaitable[User]]) -> User:
    return await user_factory()


@pytest.fixture
async def admin_user(user_factory: Callable[..., Awaitable[User]]) -> User:
    return await user_factory(
        username="admin-user",
        email="admin@example.com",
        role=UserRole.ADMIN,
    )
