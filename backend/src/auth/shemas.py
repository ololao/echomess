from pydantic import BaseModel


class AccessToken(BaseModel):
    token: str
    token_type: str = "bearer"
