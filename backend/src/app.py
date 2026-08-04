from fastapi import FastAPI

from .lifespan import lifespan
from .websockets import router

app = FastAPI(lifespan=lifespan)  # pyright: ignore[reportArgumentType]
app.include_router(router)
