from pydantic import BaseModel, Field


class User(BaseModel):
    name: str = Field(max_length=50)
