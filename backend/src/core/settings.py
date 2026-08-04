from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

parent_path = Path(__file__).parent.parent.parent.parent


class Settings(BaseSettings):
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

    def get_redis_url(self):
        return f"redis://:{self.REDIS_PASSWORD}@redis:6379/0"

    def get_db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=parent_path / ".env",
        env_file_encoding="utf-8",
    )


settings = Settings()  # pyright: ignore[reportCallIssue]
