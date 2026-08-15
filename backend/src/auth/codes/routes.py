from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import JSONResponse
from src.security import JWTTokens

from .dependency import CodeServiceDepends
from .schemas import Attempt, CodeCallbackData, LoginCreate

code_router = APIRouter()


@code_router.post("/login", status_code=200)
async def login(
    login_data: LoginCreate,
    code_service: CodeServiceDepends,
    background_tasks: BackgroundTasks,
):
    try:
        attempt_id = await code_service.login(
            email=login_data.email,
            password=login_data.password,
            background_tasks=background_tasks,
        )
        return Attempt(attempt_id=attempt_id)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@code_router.post("/code-callback", status_code=200)
async def code_callback(
    request: Request, code_service: CodeServiceDepends, callback_data: CodeCallbackData
):
    try:
        tokens: JWTTokens = await code_service.code_callback(
            code=callback_data.code, attempt_id=callback_data.attempt_id
        )
        request.session["refresh_key"] = tokens.refresh
        return JSONResponse(status_code=202, content='')
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
