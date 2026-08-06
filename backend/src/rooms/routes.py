from typing import Annotated

from fastapi import APIRouter, HTTPException, Path

from .dependency import RoomServiceDepends
from .schemas import RoomCreate

room_router = APIRouter(prefix="/room")


@room_router.post("/", status_code=201)
async def create_room(data: RoomCreate, room_service: RoomServiceDepends):
    try:
        return await room_service.create_room(name=data.name)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@room_router.get("/{id}")
async def get_room(id: Annotated[str, Path()], room_service: RoomServiceDepends):
    try:
        return await room_service.get_room(id=id)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
