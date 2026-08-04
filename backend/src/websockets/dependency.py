from typing import Annotated

from fastapi import Depends, Request

from .pubsub_listener import PubSubPublisher
from .room_manager import WebsocketRoomManager


def get_manager(request: Request):
    return WebsocketRoomManager(redis=request.app.state.redis)


type Manager = Annotated[WebsocketRoomManager, Depends(get_manager)]


def get_pubsub_listener(request: Request):
    return PubSubPublisher(redis=request.app.state.redis)


type PubSub = Annotated[PubSubPublisher, Depends(get_pubsub_listener)]
