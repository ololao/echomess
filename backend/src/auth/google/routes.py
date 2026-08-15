from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi_sso import GoogleSSO, OpenID, SSOLoginError
from src.core import settings
from src.security import JWTTokens

from .dependency import GoogleOAuthServiceDepends

google_router = APIRouter(prefix="/google")


async def get_google_sso():
    sso = GoogleSSO(
        settings.GOOGLE_CLIENT_ID,
        settings.GOOGLE_CLIENT_SECRET,
        settings.GOOGLE_REDIRECT_URL,
    )
    async with sso:
        yield sso


@google_router.get("/login")
async def google_login(
    request: Request, sso: Annotated[GoogleSSO, Depends(get_google_sso)]
):
    return await sso.get_login_redirect()


@google_router.get("/callback")
async def google_callback(
    sso: Annotated[GoogleSSO, Depends(get_google_sso)],
    request: Request,
    google_service: GoogleOAuthServiceDepends,
):

    try:
        google_user: OpenID | None = await sso.verify_and_process(request)
    except SSOLoginError:
        return RedirectResponse("/login?error=auth_failed")
    try:
        tokens: JWTTokens = await google_service.login(google_user=google_user)
        request.session["refresh_key"] = tokens.refresh
        return JSONResponse(status_code=200, content='')
    except ValueError:
        return RedirectResponse("/login?error=auth_failed")
