from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from src.core import settings


@dataclass(slots=True, kw_only=True, frozen=True)
class JWTTokens:
    access: str
    refresh: str


@dataclass(slots=True, kw_only=True, frozen=True)
class RefreshToken:
    sub: str
    session_id: str
    token_id: str
    exp: int
    token_type: str


@dataclass(slots=True, kw_only=True, frozen=True)
class AccessToken:
    sub: str
    exp: int
    token_type: str


def create_tokens(access: dict, refresh: dict):
    access_data = access.copy()
    refresh_data = refresh.copy()
    if not all([access_data.get("sub", False)]) or not all(
        [
            refresh_data.get("sub", False),
            refresh_data.get("session_id", False),
            refresh_data.get("token_id", False),
        ]
    ):
        raise ValueError("Not enough fields in to create tokens")
    access_token_exp = datetime.now(UTC) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MIN
    )
    refresh_token_exp = datetime.now(UTC) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAY
    )
    access_data.update({"exp": access_token_exp, "token_type": "access"})
    refresh_data.update({"exp": refresh_token_exp, "token_type": "refresh"})
    return JWTTokens(
        access=jwt.encode(
            access_data, key=settings.JWT_KEY, algorithm=settings.JWT_ALGORITHM
        ),
        refresh=jwt.encode(
            refresh_data, key=settings.JWT_KEY, algorithm=settings.JWT_ALGORITHM
        ),
    )


def decode_refresh_token(refresh_token: str):
    try:
        token = jwt.decode(
            refresh_token, key=settings.JWT_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise ValueError("The time of the token is over")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token format")
    sub = token.get("sub", "")
    session_id = token.get("session_id", "")
    token_id = token.get("token_id", "")
    exp = token.get("exp", "")
    token_type = token.get("token_type", "")
    if not all([sub, session_id, token_id, exp, token_type]):
        raise ValueError("Not enough fields")
    if not token_type == "refresh":
        raise ValueError("Some fields are incorrect")
    return RefreshToken(
        sub=sub,
        session_id=session_id,
        token_id=token_id,
        exp=exp,
        token_type=token_type,
    )


def decode_access_token(access_token: str):
    try:
        token = jwt.decode(
            access_token, key=settings.JWT_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise ValueError("The time of the token is over")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token format")
    sub = token.get("sub", "")
    token_type = token.get("token_type", "")
    exp = token.get("exp", "")
    if not sub:
        raise ValueError("Not enough fields")
    if not token_type == "access":
        raise ValueError("Some fields are incorrect")
    return AccessToken(sub=sub, exp=exp, token_type=token_type)
