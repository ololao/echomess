import asyncio

from src.core import logr
from src.workers import web_rooms, worker_task, worker_tasks


class WebsocketRoomManager:
    def __init__(self, redis) -> None:
        self.redis = redis

    def connect(self, room_id, websocket):
        if room_id not in worker_tasks:
            logr.info("Room_id not in worker_tasks, create worker task")
            worker_tasks[room_id] = asyncio.create_task(
                worker_task(self.redis, room_id)
            )
        web_rooms[room_id].append(websocket)

    async def disconnect(self, room_id, websocket):
        logr.info("Client is out of the room")
        if websocket in web_rooms[room_id]:
            web_rooms[room_id].remove(websocket)
        if not web_rooms[room_id]:
            del web_rooms[room_id]
            logr.info("Remove worker task")
            worker_task_obj = worker_tasks.pop(room_id, None)
            if worker_task_obj:
                try:
                    worker_task_obj.cancel()
                    await worker_task_obj
                except asyncio.CancelledError:
                    pass
