from datetime import date

from sqlalchemy import select

from src.database.db import AsyncSessionLocal, Base, engine
from src.models import User
from src.models.contact import Contact
from src.services.auth import get_password_hash


SEED_USER_EMAIL = "seed.user@example.com"
SEED_USER_PASSWORD = "seedpassword123"


async def seed_contacts() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        user_result = await session.execute(select(User).where(User.email == SEED_USER_EMAIL))
        seed_user = user_result.scalar_one_or_none()

        if seed_user is None:
            seed_user = User(
                username="seed-user",
                email=SEED_USER_EMAIL,
                hashed_password=get_password_hash(SEED_USER_PASSWORD),
                is_verified=True,
            )
            session.add(seed_user)
            await session.flush()

        test_contacts = [
            Contact(
                first_name="Ivan",
                last_name="Franko",
                email="franko@example.com",
                phone="+1234567890",
                birthday=date(1990, 5, 10),
                additional_data="Seed contact 1",
                owner_id=seed_user.id,
            ),
            Contact(
                first_name="Serhii",
                last_name="Korolov",
                email="korolov@example.com",
                phone="+1987654321",
                birthday=date(1992, 5, 14),
                additional_data="Seed contact 2",
                owner_id=seed_user.id,
            ),
            Contact(
                first_name="Hryhorii",
                last_name="Skovoroda",
                email="skovoroda@example.com",
                phone="+380501112233",
                birthday=date(2001, 5, 18),
                additional_data="Seed contact 3",
                owner_id=seed_user.id,
            ),
        ]

        result = await session.execute(select(Contact.email))
        existing_emails = set(result.scalars().all())

        contacts_to_insert = [
            contact for contact in test_contacts if contact.email not in existing_emails
        ]

        if not contacts_to_insert:
            await session.commit()
            return

        session.add_all(contacts_to_insert)
        await session.commit()


if __name__ == "__main__":
    import asyncio

    asyncio.run(seed_contacts())
