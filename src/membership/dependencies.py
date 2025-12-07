from typing import Annotated
from uuid import UUID

from fastapi import Depends, Path

from src.auth.dependencies import CurrentAccount
from src.communities.dependencies import CommunityBySlug
from src.core.database import DbSession
from src.membership.exceptions import (
    NotAMemberError,
    NotAnAdminError,
    NotOwnerError,
)
from src.membership.member_service import member_service
from src.membership.models import CommunityMember


async def get_current_member(
    db: DbSession,
    community: CommunityBySlug,
    current_account: CurrentAccount,
) -> CommunityMember:
    member = await member_service.get_by_account(db, community.id, current_account.id)
    if member is None:
        raise NotAMemberError()
    return member


async def require_active_member(
    member: Annotated[CommunityMember, Depends(get_current_member)],
) -> CommunityMember:
    if not member.is_active:
        raise NotAMemberError()
    return member


async def require_admin(
    member: Annotated[CommunityMember, Depends(require_active_member)],
) -> CommunityMember:
    if not member.is_admin:
        raise NotAnAdminError()
    return member


async def require_owner(
    member: Annotated[CommunityMember, Depends(require_active_member)],
) -> CommunityMember:
    if not member.is_owner:
        raise NotOwnerError()
    return member


async def get_member_by_id(
    db: DbSession,
    member_id: Annotated[UUID, Path(description="Member ID")],
) -> CommunityMember:
    return await member_service.get_by_id(db, member_id)


CurrentMember = Annotated[CommunityMember, Depends(get_current_member)]
RequireMember = Annotated[CommunityMember, Depends(require_active_member)]
RequireAdmin = Annotated[CommunityMember, Depends(require_admin)]
RequireOwner = Annotated[CommunityMember, Depends(require_owner)]
MemberById = Annotated[CommunityMember, Depends(get_member_by_id)]
