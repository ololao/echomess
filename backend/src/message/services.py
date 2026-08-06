from datetime import datetime

from .enums import Direction
from .repository import MessageRepository
from .schemas import MessageRead


class MessageService:
    def __init__(self, repository: MessageRepository) -> None:
        self.repository = repository

    async def get_messages_from_room(
        self,
        room_id: str,
        direction: Direction,
        limit: int,
        cursor: datetime,
    ):
        return await self.repository.get_messages_from_room(
            room_id=room_id, direction=direction, limit=limit, cursor=cursor
        )

    async def save_message(self, room_id: str, data: str, user_id: str):
        rez = await self.repository.save_message(
            room_id=room_id, data=data, user_id=user_id
        )
        return MessageRead.model_validate(rez)
