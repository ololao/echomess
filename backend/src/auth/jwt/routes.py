from fastapi import APIRouter, HTTPException, Request
from src.security import JWTTokens

from ..schemas import AccessToken
from .dependency import JwtRefresherDepends

jwt_router = APIRouter()


@jwt_router.get("/refresh", status_code=200)
async def refresh_tokens(
    request: Request,
    jwt_refresher: JwtRefresherDepends,
):
    refresh = request.session.get("refresh_key", None)
    if refresh is None:
        raise HTTPException(401)
    try:
        tokens: JWTTokens = await jwt_refresher.refresh(refresh_token=refresh)
    except ValueError:
        raise HTTPException(403)
    request.session["refresh_key"] = tokens.refresh
    return AccessToken(token=tokens.access)
