from collections.abc import AsyncGenerator, Callable

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Rooms


class RoomsRepository:
    def __init__(self, db: Callable[[], AsyncGenerator[AsyncSession, None]]):
        self.db = db

    async def create_room(self, name: str):
        query = insert(Rooms).values({"name": name}).returning(Rooms.id)
        async for db in self.db():
            room_id = await db.scalar(query)
            return room_id

    async def check_room_availability(self, id: str):
        query = select(Rooms).where(Rooms.id == id)
        async for db in self.db():
            return await db.scalar(query)

    async def get_room(self, id: str):
        query = select(Rooms).where(Rooms.id == id)
        async for db in self.db():
            return await db.scalar(query)
