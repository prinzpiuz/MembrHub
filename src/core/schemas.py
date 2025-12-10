from datetime import datetime
from typing import TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )


class TimestampSchema(BaseSchema):
    created_at: datetime
    updated_at: datetime


class BaseResponse(TimestampSchema):
    id: UUID


T = TypeVar("T")


class PaginatedResponse[T](BaseSchema):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


class MessageResponse(BaseSchema):
    message: str


class ErrorDetail(BaseSchema):
    field: str | None = None
    message: str


class ErrorResponse(BaseSchema):
    code: str
    message: str
    details: list[ErrorDetail] | None = None
