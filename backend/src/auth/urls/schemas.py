from pydantic import BaseModel, EmailStr, Field


class Registry(BaseModel):
    name: str = Field(min_length=10)
    email: EmailStr
    password: str = Field(min_length=10, max_length=25)
