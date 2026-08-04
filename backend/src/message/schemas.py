from pydantic import BaseModel, Field


class MessangeCreate(BaseModel):
    data: str = Field(max_length=1000)


class Messange(MessangeCreate):
    created_at: str
    user_id: str
