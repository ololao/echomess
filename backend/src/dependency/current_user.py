from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from src.security import decode_refresh_token
from src.users import User, UsersServiceDepends, UserStatus

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/registry")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], user_service: UsersServiceDepends
):
    token_data = decode_refresh_token(token)
    user: User | None = await user_service.get_user(user_id=token_data.sub)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


type CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_active_user(current_user: CurrentUser):
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(403)
    return current_user


type ActiveUser = Annotated[User, Depends(get_active_user)]
