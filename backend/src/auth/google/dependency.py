from typing import Annotated

from fastapi import Depends, Request
from src.auth.sessions import SessionManagerDepends
from src.users import UsersServiceDepends

from .services import GoogleOAuthService


def get_google_service(
    request: Request,
    user_service: UsersServiceDepends,
    session_manager: SessionManagerDepends,
) -> GoogleOAuthService:
    return GoogleOAuthService(
        redis=request.app.state.redis,
        user_service=user_service,
        session_manager=session_manager,
    )


type GoogleOAuthServiceDepends = Annotated[GoogleOAuthService, Depends(get_google_service)]
