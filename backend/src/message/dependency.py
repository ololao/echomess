from typing import Annotated

from fastapi import Depends, Request

from .repository import MessageRepository
from .services import MessageService


def get_message_repository(request: Request):
    return MessageRepository(db=request.app.state.db)


type MessageRepositoryDepends = Annotated[
    MessageRepository, Depends(get_message_repository)
]


def get_message_service(repository: MessageRepositoryDepends):
    return MessageService(repository=repository)


type MessageServiceDepends = Annotated[MessageService, Depends(get_message_service)]
