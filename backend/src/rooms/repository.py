from collections.abc import AsyncGenerator, Callable
from uuid import uuid4

from sqlalchemy import func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Rooms


class RoomsRepository:
    def __init__(self, db: Callable[[], AsyncGenerator[AsyncSession, None]]):
        self.db = db

    async def create_room(self, name: str) -> str:
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

    async def get_rooms(self, search: str | None, page_number: int, page_limit: int):
        query = select(Rooms)
        rank_col = None
        if search is not None:
            search = search.strip()

            if search:
                ts_query_ru = func.websearch_to_tsquery("russian", search)
                ts_query_en = func.websearch_to_tsquery("english", search)

                ts_query = ts_query_en.op("||")(ts_query_ru)

                query = query.where(Rooms.tsv.op("@@")(ts_query))

                rank_col = func.ts_rank_cd(Rooms.tsv, ts_query).label("rank")

                query = query.order_by(rank_col.desc())

        query = query.limit(page_limit).offset(page_limit * (page_number - 1))

        async for db in self.db():
            rez = await db.scalars(query)
            return rez.all()
