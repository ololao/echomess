from pydantic import BaseModel, Field


class RoomCreate(BaseModel):
    name: str = Field(min_length=3, max_length=30)
