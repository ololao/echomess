from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MessageCreate(BaseModel):
    data: str = Field(min_length=1, max_length=1000)


class MessageRead(MessageCreate):
    created_at: datetime
    user_id: str
    room_id: str
    user_name: str
    model_config = ConfigDict(from_attributes=True)
