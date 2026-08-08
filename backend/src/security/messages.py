from cryptography.fernet import Fernet

from src.core import settings

fernet = Fernet(key=settings.get_message_secret_key())


def encrypt_text(text: str) -> bytes:
    return fernet.encrypt(text.encode())


def decrypt_text(text: bytes) -> str:
    return fernet.decrypt(text).decode()
