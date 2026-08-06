from typing import Annotated

from fastapi import Depends, Request, WebSocket

from .repository import RoomsRepository
from .services import RoomsService


def get_rooms_repository(
    request: Request | None = None, websocket: WebSocket | None = None
):
    if request is None and websocket is None:
        raise ValueError("Not enough arguments!")
    if request is not None:
        return RoomsRepository(db=request.app.state.db)
    if websocket is not None:
        return RoomsRepository(db=websocket.app.state.db)


type RoomsRepositoryDepends = Annotated[RoomsRepository, Depends(get_rooms_repository)]


def get_rooms_service(repository: RoomsRepositoryDepends):
    return RoomsService(repository=repository)


type RoomServiceDepends = Annotated[RoomsService, Depends(get_rooms_service)]
