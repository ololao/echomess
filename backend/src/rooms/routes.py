from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from .dependency import RoomServiceDepends
from .schemas import Room, RoomCreate

room_router = APIRouter(prefix="/room")


@room_router.post("/", status_code=201)
async def create_room(data: RoomCreate, room_service: RoomServiceDepends) -> str:
    try:
        return await room_service.create_room(name=data.name)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@room_router.get("/", response_model=list[Room])
async def get_rooms(
    room_service: RoomServiceDepends,
    search: Annotated[str | None, Query(max_length=30)] = None,
    page_number: Annotated[int, Query(ge=1)] = 1,
    page_limit: Annotated[int, Query(ge=1, le=30)] = 30,
):
    return await room_service.get_rooms(
        search=search, page_number=page_number, page_limit=page_limit
    )
