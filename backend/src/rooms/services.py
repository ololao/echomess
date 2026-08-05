from .repository import RoomsRepository


class RoomsService:
    def __init__(self, repository: RoomsRepository):
        self.repository = repository

    async def create_room(self, name: str):
        return await self.repository.create_room(name=name)

    async def check_room_availability(self, id: str):
        return await self.repository.check_room_availability(id=id)

    async def get_room(self, id: str):
        return await self.repository.get_room(id=id)
