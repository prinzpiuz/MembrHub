from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Path, status

from src.accounts.schemas import ProfileUpdate
from src.accounts.service import account_service
from src.auth.dependencies import CurrentAccountOptional
from src.aws.ses import ses_service
from src.communities.dependencies import CommunityBySlug
from src.core.config import settings
from src.core.database import DbSession
from src.core.exceptions import ValidationError
from src.core.schemas import MessageResponse
from src.membership.dependencies import CurrentMember, RequireAdmin, RequireMember
from src.membership.exceptions import InvitationNotFoundError
from src.membership.invitation_service import invitation_service
from src.membership.member_service import member_service
from src.membership.schemas import (
    AcceptInvitationRequest,
    AddressExportResponse,
    InvitationCreate,
    InvitationDetailResponse,
    InvitationResponse,
    MemberResponse,
    MemberUpdate,
)


router = APIRouter(tags=["Membership"])


@router.post(
    "/communities/{slug}/invitations",
    response_model=InvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_invitation(
    db: DbSession,
    community: CommunityBySlug,
    current_member: RequireAdmin,
    data: InvitationCreate,
    background_tasks: BackgroundTasks,
) -> InvitationResponse:
    admin_count = await member_service.count_admins(db, community.id)
    committee_count = await member_service.count_committee(db, community.id)

    invitation = await invitation_service.create(
        db=db,
        community=community,
        data=data,
        invited_by=current_member,
        admin_count=admin_count,
        committee_count=committee_count,
    )

    invitation_link = f"{settings.CORS_ORIGINS[0]}/invitations/{invitation.token}"

    background_tasks.add_task(
        ses_service.send_invitation_email,
        to_email=invitation.email,
        community_name=community.name,
        inviter_name=current_member.account.full_name,
        role=invitation.role.value,
        invitation_link=invitation_link,
        expires_in_days=settings.INVITATION_TOKEN_EXPIRE_DAYS,
    )

    return InvitationResponse.model_validate(invitation)


@router.get(
    "/communities/{slug}/invitations",
    response_model=list[InvitationResponse],
)
async def list_invitations(
    db: DbSession,
    community: CommunityBySlug,
    _: RequireAdmin,
) -> list[InvitationResponse]:
    invitations = await invitation_service.list_pending(db, community.id)
    return [InvitationResponse.model_validate(inv) for inv in invitations]


@router.delete(
    "/communities/{slug}/invitations/{invitation_id}",
    response_model=MessageResponse,
)
async def revoke_invitation(
    db: DbSession,
    community: CommunityBySlug,
    invitation_id: Annotated[UUID, Path(description="Invitation ID")],
    _: RequireAdmin,
) -> MessageResponse:
    invitation = await invitation_service.get_by_token(db, str(invitation_id))
    if invitation.community_id != community.id:
        raise InvitationNotFoundError()

    await invitation_service.revoke(db, invitation)
    return MessageResponse(message="Invitation revoked successfully")


@router.get("/invitations/{token}", response_model=InvitationDetailResponse)
async def get_invitation(
    db: DbSession,
    token: Annotated[str, Path(description="Invitation token")],
) -> InvitationDetailResponse:
    invitation = await invitation_service.get_by_token(db, token)
    return InvitationDetailResponse.model_validate(invitation)


@router.post("/invitations/{token}/accept", response_model=MemberResponse)
async def accept_invitation(
    db: DbSession,
    token: Annotated[str, Path(description="Invitation token")],
    data: AcceptInvitationRequest,
    current_account: CurrentAccountOptional,
    background_tasks: BackgroundTasks,
) -> MemberResponse:
    invitation = await invitation_service.get_by_token(db, token)

    if current_account is None:
        if data.password is None:
            raise ValidationError("Password is required for new accounts")

        current_account = await account_service.create(
            db=db,
            email=invitation.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
        )

    member = await invitation_service.accept(db, invitation, current_account)

    background_tasks.add_task(
        ses_service.send_welcome_email,
        to_email=current_account.email,
        first_name=current_account.first_name or "there",
        community_name=invitation.community.name,
    )

    return MemberResponse.model_validate(member)


@router.get("/communities/{slug}/members", response_model=list[MemberResponse])
async def list_members(
    db: DbSession,
    community: CommunityBySlug,
    _: RequireMember,
) -> list[MemberResponse]:
    members = await member_service.list_all(db, community.id)
    return [MemberResponse.model_validate(m) for m in members]


@router.get("/communities/{slug}/members/me", response_model=MemberResponse)
async def get_my_membership(current_member: CurrentMember) -> MemberResponse:
    return MemberResponse.model_validate(current_member)


@router.patch("/communities/{slug}/members/me/profile", response_model=MemberResponse)
async def update_my_profile(
    db: DbSession,
    current_member: CurrentMember,
    data: ProfileUpdate,
) -> MemberResponse:
    await account_service.update_profile(db, current_member.account, data)
    await db.refresh(current_member)
    return MemberResponse.model_validate(current_member)


@router.post("/communities/{slug}/leave", response_model=MessageResponse)
async def leave_community(
    db: DbSession,
    current_member: CurrentMember,
) -> MessageResponse:
    await member_service.leave(db, current_member)
    return MessageResponse(message="Successfully left the community")


@router.get(
    "/communities/{slug}/members/{member_id}",
    response_model=MemberResponse,
)
async def get_member(
    db: DbSession,
    member_id: Annotated[UUID, Path(description="Member ID")],
    _: RequireMember,
) -> MemberResponse:
    member = await member_service.get_by_id(db, member_id)
    return MemberResponse.model_validate(member)


@router.patch(
    "/communities/{slug}/members/{member_id}",
    response_model=MemberResponse,
)
async def update_member(
    db: DbSession,
    community: CommunityBySlug,
    member_id: Annotated[UUID, Path(description="Member ID")],
    data: MemberUpdate,
    _: RequireAdmin,
) -> MemberResponse:
    member = await member_service.get_by_id(db, member_id)
    member = await member_service.update(db, member, data, community)
    return MemberResponse.model_validate(member)


@router.delete(
    "/communities/{slug}/members/{member_id}",
    response_model=MessageResponse,
)
async def remove_member(
    db: DbSession,
    member_id: Annotated[UUID, Path(description="Member ID")],
    _: RequireAdmin,
) -> MessageResponse:
    member = await member_service.get_by_id(db, member_id)
    await member_service.remove(db, member)
    return MessageResponse(message="Member removed successfully")


@router.get("/communities/{slug}/committee", response_model=list[MemberResponse])
async def list_committee(
    db: DbSession,
    community: CommunityBySlug,
    _: RequireMember,
) -> list[MemberResponse]:
    members = await member_service.list_committee(db, community.id)
    return [MemberResponse.model_validate(m) for m in members]


@router.get(
    "/communities/{slug}/members/export/addresses",
    response_model=AddressExportResponse,
)
async def export_addresses(
    db: DbSession,
    community: CommunityBySlug,
    _: RequireAdmin,
) -> AddressExportResponse:
    addresses = await member_service.get_formatted_addresses(db, community)
    return AddressExportResponse(addresses=addresses, total=len(addresses))
