from uuid import uuid4

from fastapi import BackgroundTasks

from src.auth.sessions import SessionManager
from src.core import settings
from src.email import EmailSender
from src.security import JWTTokens, create_fast_hash, create_tokens
from src.users import UsersService, UserStatus


def generate_url(url_token: str) -> str:
    return f"{settings.get_email_callback_url()}?token={url_token}"


class UrlService:
    def __init__(
        self,
        redis,
        user_service: UsersService,
        session_manager: SessionManager,
    ) -> None:
        self.redis = redis
        self.user_service: UsersService = user_service
        self.session_manager: SessionManager = session_manager

    async def registry(
        self, name: str, email: str, password: str, background_tasks: BackgroundTasks
    ):
        same_user = await self.user_service.get_user_by_email(email)
        if same_user is not None:
            raise ValueError("This email is already in use!")
        user_id = await self.user_service.create_user(
            name=name, email=email, password=password, status=UserStatus.PENDING
        )
        url_token = str(uuid4())
        url = generate_url(url_token)
        await self.redis.set(
            f"url-callback:{create_fast_hash(url_token)}", user_id, ex=36000
        )
        background_tasks.add_task(EmailSender.send_url, email=email, url=url)

    async def url_callback(self, token: str) -> JWTTokens:
        user_id = await self.redis.get(f"url-callback:{create_fast_hash(token)}")
        if user_id is None:
            raise ValueError("Invalid token")
        await self.user_service.change_status(user_id=user_id, status=UserStatus.ACTIVE)
        session_id = str(uuid4())
        refresh_token_id = str(uuid4())
        await self.session_manager.create_session(
            session_id=session_id, user_id=user_id, token_id=refresh_token_id
        )
        tokens: JWTTokens = create_tokens(
            access={"sub": user_id},
            refresh={
                "sub": user_id,
                "session_id": session_id,
                "token_id": refresh_token_id,
            },
        )
        return tokens
