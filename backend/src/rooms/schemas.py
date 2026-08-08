from pydantic import BaseModel, ConfigDict, Field


class RoomCreate(BaseModel):
    name: str = Field(min_length=3, max_length=30)


class Room(RoomCreate):
    id: str
    model_config = ConfigDict(from_attributes=True)
