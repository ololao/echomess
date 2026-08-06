from typing import Annotated

from fastapi import Depends, WebSocket

from src.rooms import RoomServiceDepends

from .room_manager import WebsocketRoomManager


def get_manager(websoket: WebSocket, room_service: RoomServiceDepends):
    return WebsocketRoomManager(
        redis=websoket.app.state.redis, room_service=room_service
    )


type Manager = Annotated[WebsocketRoomManager, Depends(get_manager)]
