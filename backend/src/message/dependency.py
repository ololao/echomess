from typing import Annotated

from fastapi import Depends
from fastapi.requests import HTTPConnection

from .repository import MessageRepository
from .services import MessageService


def get_message_repository(connection: HTTPConnection):
    return MessageRepository(db=connection.app.state.db)


type MessageRepositoryDepends = Annotated[
    MessageRepository, Depends(get_message_repository)
]


def get_message_service(repository: MessageRepositoryDepends):
    return MessageService(repository=repository)


type MessageServiceDepends = Annotated[MessageService, Depends(get_message_service)]
