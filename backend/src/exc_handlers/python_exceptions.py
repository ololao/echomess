from fastapi import Request
from fastapi.responses import JSONResponse


def python_exc_handler(req: Request, exc: Exception):
    return JSONResponse(status_code=500, content="Something went wrong :(" )
