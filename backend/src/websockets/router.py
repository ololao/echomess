import json

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
)
from pydantic import ValidationError

from src.core import logr
from src.dependency import ActiveUser
from src.message import MessageCreate, MessageRead, MessageServiceDepends

from .dependency import Manager

websocket_router = APIRouter(prefix="/wc")


@websocket_router.websocket("/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    manager: Manager,
    message_service: MessageServiceDepends,
    user: ActiveUser,
):
    room_key = f"room:{room_id}"
    client_host = websocket.client.host if websocket.client else "NO HOST"
    logr.info(f"WEBSOCKET --- REQUEST --- URL:{websocket.url} --- HOST:{client_host}")
    try:
        await manager.connect(room_id, websocket)
    except ValueError:
        logr.info("Room not found, error")
        raise WebSocketException(
            1000, reason="Room not found, create it before connect"
        )
    await websocket.accept()
    logr.info("Accept websocket")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                data_obj = MessageCreate.model_validate_json(data)
            except ValidationError:
                await websocket.send_json({"type": "err", "data": "Incorrecnt lenght"})
                continue
            msg: MessageRead = await message_service.save_message(
                room_id=room_id, data=data_obj.data, user_id=user.id
            )

            await websocket.app.state.redis.publish(room_key, msg.model_dump_json())
    except WebSocketDisconnect:
        pass
    finally:
        logr.info("Client is out of the room")
        await manager.disconnect(room_id, websocket)
