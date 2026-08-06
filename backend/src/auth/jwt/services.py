import json
from uuid import uuid4

from redis.asyncio import Redis

from src.core import settings
from src.security import JWTTokens, RefreshToken, create_tokens, decode_refresh_token


class JwtRefresher:
    def __init__(self, redis) -> None:
        self.redis: Redis = redis

    async def refresh(self, refresh_token: str) -> JWTTokens:
        refresh_token_obj: RefreshToken = decode_refresh_token(refresh_token)
        user_id = refresh_token_obj.sub
        session_id = refresh_token_obj.session_id
        old_data = await self.redis.get(f"session:{user_id}:{session_id}")
        if (
            old_data is None
            or (json.loads(old_data))["token_id"] != refresh_token_obj.token_id
        ):
            raise ValueError("Incorrect token")
        refresh_token_id = str(uuid4())
        data = json.dumps({"user_id": user_id, "token_id": refresh_token_id})
        await self.redis.set(
            f"session:{user_id}:{session_id}",
            data,
            ex=settings.REFRESH_TOKEN_EXPIRE_DAY * 24 * 60 * 60,
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
