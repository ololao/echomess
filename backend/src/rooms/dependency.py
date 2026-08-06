from typing import Annotated

from fastapi import Depends
from starlette.requests import HTTPConnection

from .repository import RoomsRepository
from .services import RoomsService


def get_rooms_repository(connection: HTTPConnection):
    return RoomsRepository(db=connection.app.state.db)


type RoomsRepositoryDepends = Annotated[RoomsRepository, Depends(get_rooms_repository)]


def get_rooms_service(repository: RoomsRepositoryDepends):
    return RoomsService(repository=repository)


type RoomServiceDepends = Annotated[RoomsService, Depends(get_rooms_service)]
