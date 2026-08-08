from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

parent_path = Path(__file__).parent.parent.parent.parent


class Settings(BaseSettings):
    MESSAGE_SECRET_KEY: str

    ALEMBIC_REVISION: bool = False

    REDIS_PASSWORD: str

    ACCESS_TOKEN_EXPIRE_MIN: int
    REFRESH_TOKEN_EXPIRE_DAY: int

    JWT_KEY: str
    JWT_ALGORITHM: str = "HS256"

    DEBUG: bool = False
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int = 5432
    DB_NAME: str

    DEVDB_USER: str = "admin"
    DEVDB_PASS: str | None = None
    DEVDB_HOST: str = "localhost"
    DEVDB_PORT: int = 5432
    DEVDB_NAME: str = "echomess_alembic"

    SCHEMA: str
    DOMAIN: str

    EMAIL_FROM: str
    RESEND_API_KEY: SecretStr

    COOKIE_KEY: str
    COOKIE_HTTP_ONLY: bool = False  # False for local develop

    def get_redis_url(self):
        return f"redis://:{self.REDIS_PASSWORD}@redis:6379/0"

    def get_db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def get_devdb_url(self) -> str:
        if self.DEVDB_PASS is None:
            raise ValueError("Please enter your devdb pass to use this function")
        return f"postgresql+asyncpg://{self.DEVDB_USER}:{self.DEVDB_PASS}@{self.DEVDB_HOST}:{self.DEVDB_PORT}/{self.DEVDB_NAME}"

    def get_alembic_url(self) -> str:
        if self.ALEMBIC_REVISION:
            return self.get_devdb_url()
        return self.get_db_url()

    def get_email_callback_url(self) -> str:
        return f"{self.SCHEMA}://{self.DOMAIN}/auth/url-callback"

    def get_message_secret_key(self) -> bytes:
        return (self.MESSAGE_SECRET_KEY).encode()

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=parent_path / ".env",
        env_file_encoding="utf-8",
    )


settings = Settings()  # pyright: ignore[reportCallIssue]
