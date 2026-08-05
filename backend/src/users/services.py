import asyncio

from src.security import create_password

from .enums import UserStatus
from .repository import UsersRepository


class UsersService:
    def __init__(self, repository: UsersRepository) -> None:
        self.repository: UsersRepository = repository

    async def get_user_by_email(self, email: str):
        return await self.repository.get_user_by_email(email)

    async def create_user(
        self, name: str, email: str, password: str, status: UserStatus
    ):
        hash_password = await asyncio.to_thread(create_password, password)
        return await self.repository.create_user(
            name=name, email=email, password=hash_password, status=status
        )

    async def change_status(self, user_id: str, status: UserStatus):
        return await self.repository.change_status(user_id=user_id, status=status)

    async def get_user(self, user_id: str):
        user = await self.repository.get_user(user_id=user_id)
        return user
