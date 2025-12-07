from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.communities.models import Community
from src.constants import MemberRole, MemberStatus
from src.core.config import settings
from src.membership.address import format_address
from src.membership.exceptions import (
    CannotChangeOwnerRoleError,
    CannotRemoveOwnerError,
    MaxAdminsReachedError,
    MaxCommitteeMembersReachedError,
    MemberNotFoundError,
)
from src.membership.models import CommunityMember
from src.membership.schemas import FormattedAddressResponse, MemberUpdate


class MemberService:
    async def get_by_id(
        self,
        db: AsyncSession,
        member_id: UUID,
    ) -> CommunityMember:
        result = await db.execute(
            select(CommunityMember).where(CommunityMember.id == member_id)
        )
        member = result.scalar_one_or_none()
        if member is None:
            raise MemberNotFoundError(str(member_id))
        return member

    async def get_by_account(
        self,
        db: AsyncSession,
        community_id: UUID,
        account_id: UUID,
    ) -> CommunityMember | None:
        result = await db.execute(
            select(CommunityMember).where(
                CommunityMember.community_id == community_id,
                CommunityMember.account_id == account_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_account_or_raise(
        self,
        db: AsyncSession,
        community_id: UUID,
        account_id: UUID,
    ) -> CommunityMember:
        member = await self.get_by_account(db, community_id, account_id)
        if member is None:
            raise MemberNotFoundError()
        return member

    async def list_all(
        self,
        db: AsyncSession,
        community_id: UUID,
        status: MemberStatus | None = None,
    ) -> list[CommunityMember]:
        query = select(CommunityMember).where(
            CommunityMember.community_id == community_id
        )
        if status:
            query = query.where(CommunityMember.status == status)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def list_committee(
        self,
        db: AsyncSession,
        community_id: UUID,
    ) -> list[CommunityMember]:
        result = await db.execute(
            select(CommunityMember).where(
                CommunityMember.community_id == community_id,
                CommunityMember.is_committee_member.is_(True),
                CommunityMember.status == MemberStatus.ACTIVE,
            )
        )
        return list(result.scalars().all())

    async def count_admins(self, db: AsyncSession, community_id: UUID) -> int:
        result = await db.execute(
            select(func.count(CommunityMember.id)).where(
                CommunityMember.community_id == community_id,
                CommunityMember.role.in_([MemberRole.OWNER, MemberRole.ADMIN]),
                CommunityMember.status == MemberStatus.ACTIVE,
            )
        )
        return result.scalar() or 0

    async def count_committee(self, db: AsyncSession, community_id: UUID) -> int:
        result = await db.execute(
            select(func.count(CommunityMember.id)).where(
                CommunityMember.community_id == community_id,
                CommunityMember.is_committee_member.is_(True),
                CommunityMember.status == MemberStatus.ACTIVE,
            )
        )
        return result.scalar() or 0

    async def update(
        self,
        db: AsyncSession,
        member: CommunityMember,
        data: MemberUpdate,
        community: Community,
    ) -> CommunityMember:
        await self._validate_update(db, member, data, community)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(member, field, value)

        await db.flush()
        await db.refresh(member)
        return member

    async def remove(self, db: AsyncSession, member: CommunityMember) -> None:
        if member.is_owner:
            raise CannotRemoveOwnerError()
        await db.delete(member)
        await db.flush()

    async def leave(self, db: AsyncSession, member: CommunityMember) -> None:
        await self.remove(db, member)

    async def get_formatted_addresses(
        self,
        db: AsyncSession,
        community: Community,
    ) -> list[FormattedAddressResponse]:
        members = await self.list_all(db, community.id, status=MemberStatus.ACTIVE)
        format_template = community.get_setting("address_format")

        return [
            FormattedAddressResponse(
                member_id=member.id,
                name=member.account.full_name,
                formatted_address=format_address(member.account, format_template),
            )
            for member in members
            if member.account.has_address
        ]

    async def _validate_update(
        self,
        db: AsyncSession,
        member: CommunityMember,
        data: MemberUpdate,
        community: Community,
    ) -> None:
        if member.is_owner and data.role and data.role != MemberRole.OWNER:
            raise CannotChangeOwnerRoleError()

        if data.role in (MemberRole.ADMIN, MemberRole.OWNER) and member.role not in (
            MemberRole.ADMIN,
            MemberRole.OWNER,
        ):
            admin_count = await self.count_admins(db, community.id)
            max_admins = community.get_setting(
                "max_admins", settings.MAX_ADMINS_PER_COMMUNITY
            )
            if admin_count >= max_admins:
                raise MaxAdminsReachedError(max_admins)

        if data.is_committee_member and not member.is_committee_member:
            committee_count = await self.count_committee(db, community.id)
            max_committee = community.get_setting(
                "max_committee_members", settings.MAX_COMMITTEE_MEMBERS_PER_COMMUNITY
            )
            if committee_count >= max_committee:
                raise MaxCommitteeMembersReachedError(max_committee)


member_service = MemberService()
