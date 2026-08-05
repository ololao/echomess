from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Path
from fastapi.param_functions import Query

from src.dependency import ActiveUser

from .dependency import MessageServiceDepends
from .enums import Direction
from .schemas import Messange

message_router = APIRouter(prefix="/msg")


@message_router.get("/{room_id}", status_code=200, response_model=list[Messange])
async def get_messages_from_room(
    _: ActiveUser,
    room_id: Annotated[str, Path()],  # general
    direction: Annotated[Direction, Query()],  # before | after| around
    limit: Annotated[int, Query()],  # 60
    cursor: Annotated[datetime, Query()],  # 2026-08-05T14:32:10.123Z
    message_service: MessageServiceDepends,
):
    return await message_service.get_messages_from_room(
        room_id=room_id, direction=direction, limit=limit, cursor=cursor
    )
