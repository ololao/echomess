from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Query, Request

from src.security import JWTTokens

from ..shemas import AccessToken
from .dependency import UrlServiceDepends
from .schemas import Registry

url_router = APIRouter()


@url_router.post("/registry", status_code=200)
async def registry(
    registry_data: Registry,
    url_service: UrlServiceDepends,
    background_tasks: BackgroundTasks,
):
    return await url_service.registry(
        email=registry_data.email,
        name=registry_data.name,
        password=registry_data.password,
        background_tasks=background_tasks,
    )


@url_router.get("/url-callback", status_code=200)
async def url_callback(
    request: Request, url_service: UrlServiceDepends, token: Annotated[str, Query()]
):
    tokens: JWTTokens = await url_service.url_callback(token=token)
    request.session["refresh_key"] = tokens.refresh
    return AccessToken(token=tokens.access)
