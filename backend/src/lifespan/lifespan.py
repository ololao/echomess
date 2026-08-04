from collections.abc import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core import settings


async def lifespan(app: FastAPI):
    engine = create_async_engine(
        url=settings.get_db_url(),
        echo=settings.DEBUG,
        pool_size=10,
        max_overflow=20,
    )

    SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

    async def get_db() -> AsyncGenerator[AsyncSession, None]:
        async with SessionLocal() as session:
            yield session

    async with aioredis.from_url(
        settings.get_redis_url(), decode_responses=True
    ) as redis:
        app.state.redis = redis
        app.state.db = get_db
        yield
