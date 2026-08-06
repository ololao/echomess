from collections.abc import AsyncGenerator, Callable
from datetime import datetime
from uuid import uuid4

from sqlalchemy import desc, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from .enums import Direction
from .models import Message


class MessageRepository:
    def __init__(self, db: Callable[[], AsyncGenerator[AsyncSession, None]]) -> None:
        self.db = db

    async def get_messages_from_room(
        self,
        room_id: str,
        direction: Direction,
        limit: int,
        cursor: datetime,
    ):
        query = select(Message).where(Message.room_id == room_id)
        match direction:
            case Direction.after:
                query = query.where(Message.created_at > cursor).order_by(
                    Message.created_at
                )
            case Direction.before:
                query = query.where(Message.created_at < cursor).order_by(
                    desc(Message.created_at)
                )
        query = query.limit(limit)
        async for db in self.db():
            rez = await db.scalars(query)
            return rez.all()

    async def save_message(self, room_id: str, data: str, user_id: str):
        query = (
            insert(Message)
            .values(
                {
                    "id": str(uuid4()),
                    "data": data,
                    "user_id": user_id,
                    "room_id": room_id,
                }
            )
            .returning(Message)
        )
        async for db in self.db():
            rez = await db.scalar(query)
            await db.commit()
            return rez
