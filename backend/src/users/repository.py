from ast import Call
from collections.abc import AsyncGenerator, Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User


class UsersRepository:
    def __init__(self, db: Callable[[], AsyncGenerator[AsyncSession, None]]) -> None:
        self.db = db

    async def get_user(self, user_id: str):
        query = select(User).where(User.id == user_id)
        async for db in self.db():
            user: User | None = await db.scalar(query)
            return user
