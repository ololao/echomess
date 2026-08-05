from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect

from src.core import logr
from src.dependency import ActiveUser
from src.message import MessageServiceDepends

from .dependency import Manager

websocket_router = APIRouter()


@websocket_router.websocket("/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    manager: Manager,
    request: Request,
    message_service: MessageServiceDepends,
    user: ActiveUser,
):
    room_key = f"room:{room_id}"
    client_host = websocket.client.host if websocket.client else "NO HOST"
    logr.info(f"WEBSOCKET --- REQUEST --- URL:{websocket.url} --- HOST:{client_host}")
    await websocket.accept()
    logr.info("Accept websocket")
    try:
        await manager.connect(room_id, websocket)
    except ValueError:
        raise HTTPException(404, detail="Room not found, create it before connect")
    try:
        while True:
            data = await websocket.receive_text()
            await message_service.save_message(
                room_id=room_id, data=data, user_id=user.id
            )
            await request.app.state.redis.publish(room_key, data)
    except WebSocketDisconnect:
        pass
    finally:
        logr.info("Client is out of the room")
        await manager.disconnect(room_id, websocket)
