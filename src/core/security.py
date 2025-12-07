import secrets
from datetime import UTC, datetime, timedelta
from typing import Any, cast
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.constants import TokenType
from src.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return str(pwd_context.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bool(pwd_context.verify(plain_password, hashed_password))


def create_token(
    subject: str | UUID,
    token_type: TokenType,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    if expires_delta is None:
        if token_type == TokenType.ACCESS:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        elif token_type == TokenType.REFRESH:
            expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        elif token_type == TokenType.PASSWORD_RESET:
            expires_delta = timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
        elif token_type == TokenType.EMAIL_VERIFICATION:
            expires_delta = timedelta(
                hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS
            )
        elif token_type == TokenType.INVITATION:
            expires_delta = timedelta(days=settings.INVITATION_TOKEN_EXPIRE_DAYS)
        else:
            expires_delta = timedelta(minutes=15)

    now = datetime.now(UTC)
    expire = now + expires_delta

    to_encode: dict[str, Any] = {
        "sub": str(subject),
        "type": token_type.value,
        "iat": now,
        "exp": expire,
    }

    if extra_claims:
        to_encode.update(extra_claims)

    return str(
        jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    )


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return cast(dict[str, Any], payload)
    except JWTError:
        return None


def verify_token(token: str, expected_type: TokenType) -> dict[str, Any] | None:
    payload = decode_token(token)
    if payload is None:
        return None

    token_type = payload.get("type")
    if token_type != expected_type.value:
        return None

    exp = payload.get("exp")
    if exp is None:
        return None

    if datetime.fromtimestamp(exp, tz=UTC) < datetime.now(UTC):
        return None

    return payload


def generate_secure_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def hash_token(token: str) -> str:
    import hashlib

    return hashlib.sha256(token.encode()).hexdigest()
