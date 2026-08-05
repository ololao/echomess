from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from src.auth import auth_router
from src.core import settings

from .lifespan import lifespan
from .websockets import websocket_router

app = FastAPI(lifespan=lifespan)  # pyright: ignore[reportArgumentType]
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.COOKIE_KEY,
    session_cookie="echomess_user_refresh_key",
    max_age=3600 * 24 * 14,
    same_site="lax",
    https_only=True,
)
app.include_router(websocket_router)
app.include_router(auth_router)
