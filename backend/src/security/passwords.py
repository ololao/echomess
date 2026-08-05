import hashlib
import hmac

from pwdlib import PasswordHash

from src.core import settings

password_manager: PasswordHash = PasswordHash.recommended()


def create_password(password: str):
    return password_manager.hash(password)


def check_password(password: str, hash: str):
    return password_manager.verify(password, hash)


def create_fast_hash(value: str):
    return hmac.new(
        settings.COOKIE_KEY.encode("utf-8"),
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
