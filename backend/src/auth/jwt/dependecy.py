from typing import Annotated

from fastapi import Depends, Request

from .services import JwtRefresher


def get_jwt_refresher(request: Request):
    return JwtRefresher(redis=request.app.state.redis)


type JwtRefresherDepends = Annotated[JwtRefresher, Depends(get_jwt_refresher)]
