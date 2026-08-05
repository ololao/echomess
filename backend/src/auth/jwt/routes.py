from fastapi import APIRouter, HTTPException, Request

from src.dependency import ActiveUser
from src.security import JWTTokens

from ..shemas import AccessToken
from .dependecy import JwtRefresherDepends

jwt_router = APIRouter()


@jwt_router.get("/refresh", status_code=200)
async def refresh_tokens(
    request: Request, jwt_refresher: JwtRefresherDepends, current_user: ActiveUser
):
    refresh = request.session.get("refresh_key", None)
    if refresh is None:
        raise HTTPException(401)
    tokens: JWTTokens = await jwt_refresher.refresh(refresh_token=refresh, user_id=current_user.id)
    request.session["refresh_key"] = tokens.refresh
    return AccessToken(token=tokens.access)
