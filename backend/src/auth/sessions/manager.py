import json
from uuid import uuid4

from redis.asyncio import Redis


class SessionManager:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def create_session(self, session_id: str, user_id: str, token_id: str):
        data = json.dumps({"user_id": user_id, "token_id": token_id})
        await self.redis.set(f"session:{user_id}:{session_id}", data)
        return session_id

    async def delete_session(self, user_id: str, session_id: str):
        return await self.redis.delete(f"session:{user_id}:{session_id}")
