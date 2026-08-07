from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from src.auth import auth_router
from src.core import settings
from src.message import message_router
from src.rooms import room_router

from .lifespan import lifespan
from .websockets import websocket_router

app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.COOKIE_KEY,
    session_cookie="echomess_user_refresh_key",
    max_age=3600 * 24 * 14,
    same_site="lax",
    https_only=settings.COOKIE_HTTP_ONLY,
)
app.include_router(websocket_router)
app.include_router(auth_router)
app.include_router(room_router)
app.include_router(message_router)
