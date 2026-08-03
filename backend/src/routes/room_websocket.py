import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.core import Redis, logr
from src.workers import web_rooms, worker_task, worker_tasks

router = APIRouter()


@router.websocket("/{room_id}")
async def create_websoket(
    websocket: WebSocket,
    redis: Redis,
    room_id: str,
):
    room_key = f"room:{room_id}"
    client_host = websocket.client.host if websocket.client else "NO HOST"
    logr.info(f"WEBHOOK --- REQUEST --- URL:{websocket.url} --- HOST:{client_host}")
    await websocket.accept()
    logr.info("Accept websocket")
    if room_id not in worker_tasks:
        logr.info("Room_id not in worker_tasks, create worker task")
        worker_tasks[room_id] = asyncio.create_task(worker_task(redis, room_id))
    web_rooms[room_id].append(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            payload = json.dumps(data)
            await redis.publish(room_key, payload)
    except WebSocketDisconnect:
        logr.info("Client is out of the room")
        if websocket in web_rooms[room_id]:
            web_rooms[room_id].remove(websocket)
        if not web_rooms[room_id]:
            logr.info("Remove worker task")
            worker_task_obj = worker_tasks.pop(room_id, None)
            if worker_task_obj:
                try:
                    worker_task_obj.cancel()
                    await worker_task_obj
                except asyncio.CancelledError:
                    pass
