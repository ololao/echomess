from typing import Annotated

from fastapi import Depends
from starlette.requests import HTTPConnection

from .repository import UsersRepository
from .services import UsersService


def get_users_repository(connection: HTTPConnection):
    return UsersRepository(db=connection.app.state.db)


type UsersRepositoryDepends = Annotated[UsersRepository, Depends(get_users_repository)]


def get_users_service(repository: UsersRepositoryDepends):
    return UsersService(repository=repository)


type UsersServiceDepends = Annotated[UsersService, Depends(get_users_service)]
