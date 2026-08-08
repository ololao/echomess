from typing import Annotated

from fastapi import Depends
from fastapi.requests import HTTPConnection

from src.users import UsersServiceDepends

from .repository import MessageRepository
from .services import MessageService


def get_message_repository(connection: HTTPConnection):
    return MessageRepository(db=connection.app.state.db)


type MessageRepositoryDepends = Annotated[
    MessageRepository, Depends(get_message_repository)
]


def get_message_service(
    repository: MessageRepositoryDepends, user_service: UsersServiceDepends
):
    return MessageService(repository=repository, user_service=user_service)


type MessageServiceDepends = Annotated[MessageService, Depends(get_message_service)]
