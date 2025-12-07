import re
from typing import Any
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from src.constants import CommunityType, CommunityVisibility
from src.core.schemas import BaseResponse, BaseSchema


class CommunitySettingsSchema(BaseSchema):
    max_admins: int = Field(default=3, ge=1, le=10)
    max_committee_members: int = Field(default=10, ge=1, le=50)
    address_format: str = Field(
        default="{name}\n{address_line_1}\n{address_line_2}\n{city}, {state} {postal_code}\n{country}"
    )
    allow_member_directory: bool = True
    require_profile_completion: bool = False


class CommunityCreate(BaseSchema):
    name: str = Field(..., min_length=2, max_length=255)
    slug: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = Field(None, max_length=2000)
    type: CommunityType = CommunityType.OTHER
    visibility: CommunityVisibility = CommunityVisibility.PRIVATE
    website: str | None = Field(None, max_length=500)
    registration_number: str | None = Field(None, max_length=100)

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", v):
            raise ValueError(
                "Slug must contain only lowercase letters, numbers, and hyphens"
            )
        return v

    @model_validator(mode="after")
    def generate_slug_if_missing(self) -> CommunityCreate:
        if self.slug is None:
            self.slug = re.sub(r"[^a-z0-9]+", "-", self.name.lower()).strip("-")
        return self


class CommunityUpdate(BaseSchema):
    name: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = Field(None, max_length=2000)
    type: CommunityType | None = None
    visibility: CommunityVisibility | None = None
    website: str | None = Field(None, max_length=500)
    registration_number: str | None = Field(None, max_length=100)


class CommunitySettingsUpdate(BaseSchema):
    max_admins: int | None = Field(None, ge=1, le=10)
    max_committee_members: int | None = Field(None, ge=1, le=50)
    address_format: str | None = None
    allow_member_directory: bool | None = None
    require_profile_completion: bool | None = None


class CommunityResponse(BaseResponse):
    name: str
    slug: str
    description: str | None = None
    type: CommunityType
    visibility: CommunityVisibility
    website: str | None = None
    registration_number: str | None = None
    bylaws_url: str | None = None
    logo_url: str | None = None
    banner_url: str | None = None
    settings: dict[str, Any]
    created_by: UUID
    is_active: bool


class CommunityBriefResponse(BaseSchema):
    id: UUID
    name: str
    slug: str
    type: CommunityType
    logo_url: str | None = None
