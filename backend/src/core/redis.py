from typing import Annotated

import redis.asyncio as aioredis
from fastapi import Depends

from .settings import settings


async def get_redis():
    async with aioredis.from_url(settings.get_redis_url()) as redis:
        yield redis


type Redis = Annotated[aioredis.Redis, Depends(get_redis)]
