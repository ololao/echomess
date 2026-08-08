from datetime import datetime

from src.security import decrypt_text, encrypt_text
from src.users import UsersService

from .enums import Direction
from .repository import MessageRepository
from .schemas import MessageRead


class MessageService:
    def __init__(
        self, repository: MessageRepository, user_service: UsersService
    ) -> None:
        self.repository = repository
        self.user_service = user_service

    async def get_messages_from_room(
        self,
        room_id: str,
        direction: Direction,
        limit: int,
        cursor: datetime,
    ) -> list[MessageRead] | None:
        rez = await self.repository.get_messages_from_room(
            room_id=room_id, direction=direction, limit=limit, cursor=cursor
        )
        if rez is not None:
            return [
                MessageRead(
                    data=decrypt_text(x.data),
                    created_at=x.created_at,
                    user_id=x.user_id,
                    room_id=x.room_id,
                    user_name=x.user.name,
                )
                for x in rez
            ]
        return rez

    async def save_message(self, room_id: str, data: str, user_id: str) -> MessageRead:
        byte_data = encrypt_text(data)
        rez = await self.repository.save_message(
            room_id=room_id, data=byte_data, user_id=user_id
        )
        if rez is None:
            raise ValueError("Failed to save the message!")
        user_name = await self.user_service.get_user(user_id=rez.user_id)
        return MessageRead(
            data=decrypt_text(rez.data),
            created_at=rez.created_at,
            user_id=rez.user_id,
            room_id=rez.room_id,
            user_name=(user_name.name if user_name is not None else "DELETED USER"),
        )
