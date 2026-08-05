from fastapi import APIRouter, BackgroundTasks, Request

from src.security import JWTTokens

from ..shemas import AccessToken
from .dependency import CodeServiceDepends
from .schemas import Attempt, CodeCallbackData, LoginCreate

code_router = APIRouter()


@code_router.post("/login", status_code=200)
async def registry(
    login_data: LoginCreate,
    code_service: CodeServiceDepends,
    background_tasks: BackgroundTasks,
):
    attempt_id = await code_service.login(
        email=login_data.email,
        password=login_data.password,
        background_tasks=background_tasks,
    )
    return Attempt(attempt_id=attempt_id)


@code_router.post("/code-callback", status_code=200)
async def url_callback(
    request: Request, code_service: CodeServiceDepends, callback_data: CodeCallbackData
):
    tokens: JWTTokens = await code_service.code_callback(
        code=callback_data.code, attempt_id=callback_data.attempt_id
    )
    request.session["refresh_key"] = tokens.refresh
    return AccessToken(token=tokens.access)
