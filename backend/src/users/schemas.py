from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(max_length=10)
    email: EmailStr
    password: str = Field(min_length=10, max_length=25)


class UserLogIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=25)


class User(BaseModel):
    name: str = Field(max_length=10)
