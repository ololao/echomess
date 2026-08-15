from collections.abc import AsyncGenerator, Callable
from uuid import uuid4

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from .enums import UserStatus
from .models import User


class UsersRepository:
    def __init__(self, db: Callable[[], AsyncGenerator[AsyncSession, None]]) -> None:
        self.db = db

    async def get_user_by_email(self, email: str):
        query = select(User).where(User.email == email)
        async for db in self.db():
            user: User | None = await db.scalar(query)
            return user

    async def create_user(
        self, name: str, email: str, password: str, status: UserStatus
    ):
        user_id = str(uuid4())
        query = (
            insert(User)
            .values(
                {
                    "id": user_id,
                    "name": name,
                    "email": email,
                    "password": password,
                    "status": status,
                }
            )
            .returning(User.id)
        )
        async for db in self.db():
            await db.execute(query)
            await db.commit()
            return user_id

    async def create_google_user(
        self, name: str, email: str, google_id: str, status: UserStatus
    ):
        user_id = str(uuid4())
        query = (
            insert(User)
            .values(
                {
                    "id": user_id,
                    "name": name,
                    "email": email,
                    "google_id": google_id,
                    "status": status,
                }
            )
            .returning(User.id)
        )
        async for db in self.db():
            await db.execute(query)
            await db.commit()
            return user_id

    async def change_status(self, user_id: str, status: UserStatus):
        query = select(User).where(User.id == user_id)
        async for db in self.db():
            user: User | None = await db.scalar(query)
            if user is None:
                raise ValueError("User not found")
            user.status = status
            await db.commit()
            return user

    async def get_user(self, user_id: str):
        query = select(User).where(User.id == user_id)
        async for db in self.db():
            user: User | None = await db.scalar(query)
            return user

    async def get_google_user(self, google_id: str):
        query = select(User).where(User.google_id == google_id)
        async for db in self.db():
            user: User | None = await db.scalar(query)
            return user
