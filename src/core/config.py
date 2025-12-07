from functools import lru_cache
from typing import Annotated, cast

from pydantic import (
    BeforeValidator,
    Field,
    PostgresDsn,
    computed_field,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL, make_url

from src.constants import Environment


def parse_cors_origins(v: str | list[str]) -> list[str]:
    if isinstance(v, str):
        return [origin.strip() for origin in v.strip("[]").split(",")]
    return v


CorsOrigins = Annotated[list[str], BeforeValidator(parse_cors_origins)]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    ENVIRONMENT: Environment = Environment.LOCAL
    DEBUG: bool = False
    APP_VERSION: str = "0.1.0"
    APP_NAME: str = "MembrrHub"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: PostgresDsn = Field(
        default=cast(
            PostgresDsn,
            "postgresql+asyncpg://postgres:postgres@localhost:5432/membrhub",
        )
    )

    SECRET_KEY: str = Field(
        default="your-super-secret-key-change-in-production-min-32-chars"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 1
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24
    INVITATION_TOKEN_EXPIRE_DAYS: int = 7

    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None

    SES_FROM_EMAIL: str = "noreply@membrhub.com"
    SES_FROM_NAME: str = "MembrrHub"

    S3_BUCKET_NAME: str = "membrhub-files"
    S3_PRESIGNED_URL_EXPIRY: int = 3600

    CORS_ORIGINS: CorsOrigins = ["http://localhost:3000"]
    CORS_HEADERS: list[str] = ["*"]
    CORS_METHODS: list[str] = ["*"]

    RATE_LIMIT_PER_MINUTE: int = 60

    MAX_ADMINS_PER_COMMUNITY: int = 3
    MAX_COMMITTEE_MEMBERS_PER_COMMUNITY: int = 10

    @computed_field
    def async_database_url(self) -> URL:
        return make_url(str(self.DATABASE_URL))

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT in (Environment.LOCAL, Environment.TESTING)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
