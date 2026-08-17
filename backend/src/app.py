from fastapi import FastAPI
from src.auth import auth_router
from src.core import settings
from src.exc_handlers import registrar
from src.message import message_router
from src.middleware import LogerMiddleware
from src.rooms import room_router
from starlette.middleware.sessions import SessionMiddleware

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
app.add_middleware(LogerMiddleware)
app.include_router(websocket_router)
app.include_router(auth_router)
app.include_router(room_router)
app.include_router(message_router)
registrar(app)