

from uuid import uuid4

from fastapi import Request
from src.core import request_id


async def logger_middleware(request: Request, call_next):
    request_id.set(str(uuid4()))
    responce = await call_next(request)
    return responce