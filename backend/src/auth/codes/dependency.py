from typing import Annotated

from fastapi import Depends, Request

from src.auth.sessions import SessionManagerDepends
from src.users import UsersServiceDepends

from .services import CodeService


def get_code_service(
    request: Request,
    user_service: UsersServiceDepends,
    session_manager: SessionManagerDepends,
):
    return CodeService(
        redis=request.app.state.redis,
        user_service=user_service,
        session_manager=session_manager,
    )


type CodeServiceDepends = Annotated[CodeService, Depends(get_code_service)]
