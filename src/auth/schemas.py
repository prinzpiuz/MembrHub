from pydantic import EmailStr, Field

from src.core.schemas import BaseSchema


TOKEN_TYPE_BEARER = "bearer"  # noqa: S105


class RegisterRequest(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = TOKEN_TYPE_BEARER


class AccessTokenResponse(BaseSchema):
    access_token: str
    token_type: str = TOKEN_TYPE_BEARER


class RefreshTokenRequest(BaseSchema):
    refresh_token: str


class ForgotPasswordRequest(BaseSchema):
    email: EmailStr


class ResetPasswordRequest(BaseSchema):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class VerifyEmailRequest(BaseSchema):
    token: str
