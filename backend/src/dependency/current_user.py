from typing import Annotated, NoReturn

from fastapi import Depends, HTTPException, WebSocketException, status
from src.core import user_id
from src.security import decode_access_token
from src.users import User, UsersServiceDepends, UserStatus
from starlette.requests import HTTPConnection


def raise_not_authenticated(connection: HTTPConnection) -> NoReturn:
    if connection.scope["type"] == "websocket":
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_bearer_token(connection: HTTPConnection):
    authorization: str | None = connection.headers.get("Authorization", None)
    if authorization is None:
        raise_not_authenticated(connection)
        return
    scheme, token = authorization.split()
    if scheme.lower() == "bearer" and token:
        return token
    raise_not_authenticated(connection)


async def get_current_user(
    connection: HTTPConnection,
    token: Annotated[str, Depends(get_bearer_token)],
    user_service: UsersServiceDepends,
):
        try:
            token_data = decode_access_token(token)
        except ValueError:
            raise HTTPException(401)
        user: User | None = await user_service.get_user(user_id=token_data.sub)
        if user is None:
            raise_not_authenticated(connection)
        try:
            context_token = user_id.set(user.id)
            yield user
        finally:
            user_id.reset(context_token)

type CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_active_user(current_user: CurrentUser):
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(403)
    return current_user


type ActiveUser = Annotated[User, Depends(get_active_user)]
