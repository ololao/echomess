from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from src.core import settings

from .lifespan import lifespan
from .websockets import router

app = FastAPI(lifespan=lifespan)  # pyright: ignore[reportArgumentType]
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.COOKIE_KEY,
    session_cookie="echomess_user_refresh_key",
    max_age=3600 * 24 * 14,
    same_site="lax",
    https_only=True,
)
app.include_router(router)
