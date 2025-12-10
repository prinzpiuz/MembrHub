from datetime import date, datetime
from uuid import UUID

from pydantic import EmailStr, Field

from src.core.schemas import BaseResponse, BaseSchema


class AddressSchema(BaseSchema):
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None


class ProfileUpdate(BaseSchema):
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    phone: str | None = Field(None, max_length=20)
    date_of_birth: date | None = None
    address_line_1: str | None = Field(None, max_length=255)
    address_line_2: str | None = Field(None, max_length=255)
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=100)
    postal_code: str | None = Field(None, max_length=20)
    country: str | None = Field(None, max_length=100)


class PasswordChange(BaseSchema):
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8, max_length=128)


class AccountResponse(BaseResponse):
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    date_of_birth: date | None = None
    avatar_url: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    is_active: bool
    is_verified: bool
    last_login_at: datetime | None = None


class AccountBriefResponse(BaseSchema):
    id: UUID
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None

    @property
    def full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.email
