from pydantic import BaseModel, EmailStr, Field


class LoginCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=25)


class Attempt(BaseModel):
    attempt_id: str


class CodeCallbackData(Attempt):
    code: str
