from typing import Annotated

from fastapi import Depends, Request

from .manager import SessionManager


def get_session_manager(request: Request):
    return SessionManager(redis=request.app.state.redis)


type SessionManagerDepends = Annotated[SessionManager, Depends(get_session_manager)]
