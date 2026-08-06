from collections.abc import AsyncGenerator, Callable
from uuid import uuid4

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Rooms


class RoomsRepository:
    def __init__(self, db: Callable[[], AsyncGenerator[AsyncSession, None]]):
        self.db = db

    async def create_room(self, name: str):
        room_id = str(uuid4())
        query = insert(Rooms).values({"id": room_id, "name": name})
        async for db in self.db():
            await db.execute(query)
            await db.commit()
            return room_id

    async def check_room_availability(self, id: str):
        query = select(Rooms).where(Rooms.id == id)
        async for db in self.db():
            return await db.scalar(query)

    async def get_room(self, id: str):
        query = select(Rooms).where(Rooms.id == id)
        async for db in self.db():
            return await db.scalar(query)
