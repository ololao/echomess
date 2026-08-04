from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    name: str = Field(max_length=10)
