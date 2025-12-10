from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field

from src.accounts.schemas import AccountBriefResponse
from src.communities.schemas import CommunityBriefResponse
from src.constants import MemberRole, MemberStatus
from src.core.schemas import BaseResponse, BaseSchema


class InvitationCreate(BaseSchema):
    email: EmailStr
    role: MemberRole = MemberRole.MEMBER
    is_committee_member: bool = False


class InvitationResponse(BaseResponse):
    community_id: UUID
    email: EmailStr
    role: MemberRole
    is_committee_member: bool
    expires_at: datetime
    accepted_at: datetime | None = None


class InvitationDetailResponse(InvitationResponse):
    community: CommunityBriefResponse


class MemberUpdate(BaseSchema):
    role: MemberRole | None = None
    status: MemberStatus | None = None
    is_committee_member: bool | None = None


class MemberResponse(BaseResponse):
    community_id: UUID
    account_id: UUID
    role: MemberRole
    status: MemberStatus
    is_committee_member: bool
    joined_at: datetime | None = None
    account: AccountBriefResponse


class MemberBriefResponse(BaseSchema):
    id: UUID
    role: MemberRole
    status: MemberStatus
    is_committee_member: bool
    account: AccountBriefResponse


class MemberWithCommunityResponse(MemberResponse):
    community: CommunityBriefResponse


class AcceptInvitationRequest(BaseSchema):
    password: str | None = Field(None, min_length=8, max_length=128)
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)


class FormattedAddressResponse(BaseSchema):
    member_id: UUID
    name: str
    formatted_address: str


class AddressExportResponse(BaseSchema):
    addresses: list[FormattedAddressResponse]
    total: int
