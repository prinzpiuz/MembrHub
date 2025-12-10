from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.accounts.models import Account
from src.communities.models import Community
from src.constants import MemberRole, MemberStatus
from src.core.config import settings
from src.core.security import generate_secure_token
from src.membership.exceptions import (
    AlreadyMemberError,
    InvitationAlreadyAcceptedError,
    InvitationAlreadyExistsError,
    InvitationExpiredError,
    InvitationNotFoundError,
    MaxAdminsReachedError,
    MaxCommitteeMembersReachedError,
)
from src.membership.models import CommunityInvitation, CommunityMember
from src.membership.schemas import InvitationCreate


class InvitationService:
    async def get_by_token(
        self,
        db: AsyncSession,
        token: str,
    ) -> CommunityInvitation:
        result = await db.execute(
            select(CommunityInvitation).where(CommunityInvitation.token == token)
        )
        invitation = result.scalar_one_or_none()
        if invitation is None:
            raise InvitationNotFoundError()
        return invitation

    async def list_pending(
        self,
        db: AsyncSession,
        community_id: UUID,
    ) -> list[CommunityInvitation]:
        result = await db.execute(
            select(CommunityInvitation).where(
                CommunityInvitation.community_id == community_id,
                CommunityInvitation.accepted_at.is_(None),
                CommunityInvitation.expires_at > datetime.now(UTC),
            )
        )
        return list(result.scalars().all())

    async def create(
        self,
        db: AsyncSession,
        community: Community,
        data: InvitationCreate,
        invited_by: CommunityMember,
        admin_count: int,
        committee_count: int,
    ) -> CommunityInvitation:
        await self._validate_no_existing_member(db, community.id, data.email)
        await self._validate_no_pending_invitation(db, community.id, data.email)
        self._validate_admin_limit(data.role, admin_count, community)
        self._validate_committee_limit(
            data.is_committee_member, committee_count, community
        )

        token = generate_secure_token()
        expires_at = datetime.now(UTC) + timedelta(
            days=settings.INVITATION_TOKEN_EXPIRE_DAYS
        )

        invitation = CommunityInvitation(
            community_id=community.id,
            email=data.email.lower(),
            role=data.role,
            is_committee_member=data.is_committee_member,
            token=token,
            invited_by=invited_by.id,
            expires_at=expires_at,
        )
        db.add(invitation)
        await db.flush()
        await db.refresh(invitation)
        return invitation

    async def accept(
        self,
        db: AsyncSession,
        invitation: CommunityInvitation,
        account: Account,
    ) -> CommunityMember:
        if invitation.is_accepted:
            raise InvitationAlreadyAcceptedError()
        if invitation.is_expired:
            raise InvitationExpiredError()

        member = CommunityMember(
            community_id=invitation.community_id,
            account_id=account.id,
            role=invitation.role,
            status=MemberStatus.ACTIVE,
            is_committee_member=invitation.is_committee_member,
            invited_by=invitation.invited_by,
            joined_at=datetime.now(UTC),
        )
        db.add(member)

        invitation.accepted_at = datetime.now(UTC)

        await db.flush()
        await db.refresh(member)
        return member

    async def revoke(
        self,
        db: AsyncSession,
        invitation: CommunityInvitation,
    ) -> None:
        await db.delete(invitation)
        await db.flush()

    async def _validate_no_existing_member(
        self,
        db: AsyncSession,
        community_id: UUID,
        email: str,
    ) -> None:
        result = await db.execute(
            select(CommunityMember)
            .join(Account)
            .where(
                CommunityMember.community_id == community_id,
                Account.email == email.lower(),
            )
        )
        if result.scalar_one_or_none():
            raise AlreadyMemberError(email)

    async def _validate_no_pending_invitation(
        self,
        db: AsyncSession,
        community_id: UUID,
        email: str,
    ) -> None:
        result = await db.execute(
            select(CommunityInvitation).where(
                CommunityInvitation.community_id == community_id,
                CommunityInvitation.email == email.lower(),
                CommunityInvitation.accepted_at.is_(None),
                CommunityInvitation.expires_at > datetime.now(UTC),
            )
        )
        if result.scalar_one_or_none():
            raise InvitationAlreadyExistsError(email)

    def _validate_admin_limit(
        self,
        role: MemberRole,
        current_count: int,
        community: Community,
    ) -> None:
        if role not in (MemberRole.ADMIN, MemberRole.OWNER):
            return
        max_admins = community.get_setting(
            "max_admins", settings.MAX_ADMINS_PER_COMMUNITY
        )
        if current_count >= max_admins:
            raise MaxAdminsReachedError(max_admins)

    def _validate_committee_limit(
        self,
        is_committee: bool,
        current_count: int,
        community: Community,
    ) -> None:
        if not is_committee:
            return
        max_committee = community.get_setting(
            "max_committee_members", settings.MAX_COMMITTEE_MEMBERS_PER_COMMUNITY
        )
        if current_count >= max_committee:
            raise MaxCommitteeMembersReachedError(max_committee)


invitation_service = InvitationService()
