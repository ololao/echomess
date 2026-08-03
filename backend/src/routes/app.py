from fastapi import FastAPI

from .room_websocket import router

app = FastAPI()
app.include_router(router)
