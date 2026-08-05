from typing import Annotated

from fastapi import Depends, Request

from src.auth.sessions import SessionManagerDepends
from src.users import UsersServiceDepends

from .services import UrlService


def get_url_service(
    request: Request,
    user_service: UsersServiceDepends,
    session_manager: SessionManagerDepends,
):
    return UrlService(
        redis=request.app.state.redis,
        user_service=user_service,
        session_manager=session_manager,
    )


type UrlServiceDepends = Annotated[UrlService, Depends(get_url_service)]
