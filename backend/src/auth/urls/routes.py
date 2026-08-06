from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from src.security import JWTTokens

from ..schemas import AccessToken
from .dependency import UrlServiceDepends
from .schemas import Registry

url_router = APIRouter()


@url_router.post("/registry", status_code=200)
async def registry(
    registry_data: Registry,
    url_service: UrlServiceDepends,
    background_tasks: BackgroundTasks,
):
    try:
        return await url_service.registry(
            email=registry_data.email,
            name=registry_data.name,
            password=registry_data.password,
            background_tasks=background_tasks,
        )
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@url_router.get("/url-callback", status_code=200)
async def url_callback(
    request: Request, url_service: UrlServiceDepends, token: Annotated[str, Query()]
):
    try:
        tokens: JWTTokens = await url_service.url_callback(token=token)
        request.session["refresh_key"] = tokens.refresh
        return AccessToken(token=tokens.access)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
