import json
from random import randrange
from uuid import uuid4

from fastapi import BackgroundTasks

from src.auth.sessions import SessionManager
from src.email import EmailSender
from src.security import JWTTokens, check_password, create_password, create_tokens
from src.users import UsersService, UserStatus


class CodeService:
    def __init__(
        self,
        redis,
        user_service: UsersService,
        session_manager: SessionManager,
    ) -> None:
        self.redis = redis
        self.user_service: UsersService = user_service
        self.session_manager: SessionManager = session_manager

    async def login(self, email: str, password: str, background_tasks: BackgroundTasks):
        same_user = await self.user_service.get_user_by_email(email)
        if same_user is None or same_user.status != UserStatus.ACTIVE:
            raise ValueError("This user does not exist")
        if not all(
            [same_user.email == email, check_password(password, same_user.password)]
        ):
            raise ValueError("Incorrect login details")
        code = str(randrange(100000, 1000000))
        hash_code = create_password(code)
        attempt_id = str(uuid4())
        callback_data = json.dumps({"code": hash_code, "user_id": same_user.id})
        await self.redis.set(
            f"code-callback:{attempt_id}", callback_data, ex=300
        )  # frontend save attempt to storage
        background_tasks.add_task(EmailSender.send_code, email=email, code=code)
        return attempt_id

    async def code_callback(self, attempt_id: str, code: str):
        rawdata = await self.redis.get(f"code-callback:{attempt_id}")
        if rawdata is None:
            raise ValueError("Incorrect login details")
        callback_data = json.loads(rawdata)
        if not check_password(code, callback_data["code"]):
            raise ValueError("Incorrect code, please try again")
        await self.redis.delete(f"code-callback:{attempt_id}")
        user_id = callback_data["user_id"]
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
