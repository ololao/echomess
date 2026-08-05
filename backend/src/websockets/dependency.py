from typing import Annotated

from fastapi import Depends, Request

from .room_manager import WebsocketRoomManager


def get_manager(request: Request):
    return WebsocketRoomManager(redis=request.app.state.redis)


type Manager = Annotated[WebsocketRoomManager, Depends(get_manager)]
