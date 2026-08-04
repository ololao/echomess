from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

parent_path = Path(__file__).parent.parent.parent.parent


class Settings(BaseSettings):
    REDIS_PASSWORD: str

    ACCESS_TOKEN_EXPIRE_MIN: int
    REFRESH_TOKEN_EXPIRE_DAY: int

    JWT_KEY: str
    JWT_ALGORITHM:str = 'HS256'

    def get_redis_url(self):
        return f"redis://:{self.REDIS_PASSWORD}@redis:6379/0"

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=parent_path / ".env",
        env_file_encoding="utf-8",
    )


settings = Settings()  # pyright: ignore[reportCallIssue]
