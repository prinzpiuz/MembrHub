from src.core.config import settings


class AuthConfig:
    SECRET_KEY: str = settings.SECRET_KEY
    ALGORITHM: str = settings.JWT_ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_DAYS: int = settings.REFRESH_TOKEN_EXPIRE_DAYS
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS


auth_config = AuthConfig()
