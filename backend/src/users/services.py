from .repository import UsersRepository


class UsersService:
    def __init__(self, repository: UsersRepository) -> None:
        self.repository: UsersRepository = repository

    async def get_user(self, user_id: str):
        return await self.repository.get_user(user_id)
