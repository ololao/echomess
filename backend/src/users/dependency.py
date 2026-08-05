from typing import Annotated

from fastapi import Depends, Request

from .repository import UsersRepository
from .services import UsersService


def get_users_repository(request: Request):
    return UsersRepository(db=request.app.state.db)


type UsersRepositoryDepends = Annotated[UsersRepository, Depends(get_users_repository)]


def get_users_service(repository: UsersRepositoryDepends):
    return UsersService(repository=repository)


type UsersServiceDepends = Annotated[UsersService, Depends(get_users_service)]
