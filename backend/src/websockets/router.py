from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.core import logr

from .dependency import Manager, PubSub

router = APIRouter()


@router.websocket("/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    manager: Manager,
    pubsub: PubSub,
):
    room_key = f"room:{room_id}"
    client_host = websocket.client.host if websocket.client else "NO HOST"
    logr.info(f"WEBSOCKET --- REQUEST --- URL:{websocket.url} --- HOST:{client_host}")
    await websocket.accept()
    logr.info("Accept websocket")
    manager.connect(room_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await pubsub.publish(room_key, data)
    except WebSocketDisconnect:
        pass
    finally:
        logr.info("Client is out of the room")
        await manager.disconnect(room_id, websocket)
