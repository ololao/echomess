from uuid import uuid4

from fastapi_sso import OpenID
from redis.asyncio import Redis
from src.auth.sessions import SessionManager
from src.security import (
    JWTTokens,
    create_tokens,
)
from src.users import UsersService, UserStatus
from src.users.models import User


class GoogleOAuthService:
    def __init__(
        self,
        redis,
        user_service: UsersService,
        session_manager: SessionManager,
    ) -> None:
        self.redis: Redis = redis
        self.user_service: UsersService = user_service
        self.session_manager: SessionManager = session_manager

    async def login(self, google_user: OpenID | None) -> JWTTokens:
        if (
            google_user is None
            or google_user.email is None
            or google_user.display_name is None
            or google_user.id is None
        ):
            raise ValueError("Incorrect Google Account data")

        same_user: User | None = await self.user_service.get_user_by_email(
            str(google_user.email)
        )
        if same_user is not None:
            if same_user.status == UserStatus.INACTIVE:
                raise ValueError("This user is banned")
            if same_user.status == UserStatus.PENDING:
                raise ValueError("You have already started another registration")
            current_user: User = same_user
        else:
            user_id = await self.user_service.create_google_user(
                name=google_user.display_name,
                email=str(google_user.email),
                google_id=google_user.id,
            )
            assert user_id is not None
            new_google_user = await self.user_service.get_google_user(
                google_id=google_user.id
            )
            assert new_google_user is not None
            current_user: User = new_google_user
        session_id = str(uuid4())
        refresh_token_id = str(uuid4())
        user_session_age = await self.redis.get(f"user_session_age:{current_user.id}")
        if not isinstance(user_session_age, str):
            user_session_age = "0"
        await self.session_manager.create_session(
            session_id=session_id,
            user_id=current_user.id,
            token_id=refresh_token_id,
            session_age=user_session_age,
        )
        tokens: JWTTokens = create_tokens(
            access={"sub": current_user.id},
            refresh={
                "sub": current_user.id,
                "session_id": session_id,
                "token_id": refresh_token_id,
            },
        )
        return tokens
