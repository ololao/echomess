from redis.asyncio import Redis


class PubSubPublisher:
    def __init__(self, redis) -> None:
        self.redis: Redis = redis

    async def publish(self, room_key: str, payload: str):
        await self.redis.publish(room_key, payload)
