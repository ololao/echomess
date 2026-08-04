import redis.asyncio as aioredis
from fastapi import FastAPI

from src.core import settings


async def lifespan(app: FastAPI):
    async with aioredis.from_url(
        settings.get_redis_url(), decode_responses=True
    ) as redis:
        app.state.redis = redis
        yield
