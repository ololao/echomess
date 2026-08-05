from typing import Annotated

from fastapi import Depends, Request

from src.rooms import RoomServiceDepends

from .room_manager import WebsocketRoomManager


def get_manager(request: Request, room_service: RoomServiceDepends):
    return WebsocketRoomManager(
        redis=request.app.state.redis, room_service=room_service
    )


type Manager = Annotated[WebsocketRoomManager, Depends(get_manager)]
