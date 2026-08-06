from asyncio import CancelledError, Event
from asyncio.tasks import Task

from fastapi import WebSocket
from redis.asyncio import Redis

from src.core import logr

web_rooms: dict[str, list[WebSocket]] = {}
worker_tasks: dict[str, Task] = {}


async def worker_task(redis: Redis, room_id: str, event: Event):
    room_key = f"room:{room_id}"
    async with redis.pubsub() as pubsub:
        await pubsub.subscribe(room_key)
        event.set()
        try:
            async for message in pubsub.listen():
                if message["type"] == "message" and room_id in web_rooms:
                    for wb in list(web_rooms[room_id]):
                        try:
                            await wb.send_text(message["data"])
                        except Exception as e:
                            web_rooms[room_id].remove(wb)
                            logr.error(f"Worker Task await wb.send_text Error - {e}")
        except CancelledError:
            logr.info("Task cancelled, unsubscribe")
            await pubsub.unsubscribe(room_key)
