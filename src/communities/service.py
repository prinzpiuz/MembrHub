from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.communities.exceptions import (
    CommunityNotFoundError,
    CommunitySlugExistsError,
)
from src.communities.models import Community
from src.communities.schemas import (
    CommunityCreate,
    CommunitySettingsSchema,
    CommunitySettingsUpdate,
    CommunityUpdate,
)
from src.constants import MemberRole, MemberStatus
from src.membership.models import CommunityMember


class CommunityService:
    async def get_by_id(self, db: AsyncSession, community_id: UUID) -> Community:
        result = await db.execute(
            select(Community).where(
                Community.id == community_id,
                Community.deleted_at.is_(None),
            )
        )
        community = result.scalar_one_or_none()
        if community is None:
            raise CommunityNotFoundError(str(community_id))
        return community

    async def get_by_slug(self, db: AsyncSession, slug: str) -> Community:
        result = await db.execute(
            select(Community).where(
                Community.slug == slug.lower(),
                Community.deleted_at.is_(None),
            )
        )
        community = result.scalar_one_or_none()
        if community is None:
            raise CommunityNotFoundError(slug)
        return community

    async def get_by_slug_optional(
        self,
        db: AsyncSession,
        slug: str,
    ) -> Community | None:
        result = await db.execute(
            select(Community).where(
                Community.slug == slug.lower(),
                Community.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        data: CommunityCreate,
        created_by: UUID,
    ) -> Community:
        assert data.slug is not None
        existing = await self.get_by_slug_optional(db, data.slug)
        if existing:
            raise CommunitySlugExistsError(data.slug)

        default_settings = CommunitySettingsSchema().model_dump()

        community = Community(
            name=data.name,
            slug=data.slug.lower(),
            description=data.description,
            type=data.type,
            visibility=data.visibility,
            website=data.website,
            registration_number=data.registration_number,
            settings=default_settings,
            created_by=created_by,
        )
        db.add(community)
        await db.flush()

        owner_member = CommunityMember(
            community_id=community.id,
            account_id=created_by,
            role=MemberRole.OWNER,
            status=MemberStatus.ACTIVE,
        )
        db.add(owner_member)
        await db.flush()

        await db.refresh(community)
        return community

    async def update(
        self,
        db: AsyncSession,
        community: Community,
        data: CommunityUpdate,
    ) -> Community:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(community, field, value)

        await db.flush()
        await db.refresh(community)
        return community

    async def update_settings(
        self,
        db: AsyncSession,
        community: Community,
        data: CommunitySettingsUpdate,
    ) -> Community:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            community.settings[key] = value

        await db.flush()
        await db.refresh(community)
        return community

    async def update_logo(
        self,
        db: AsyncSession,
        community: Community,
        logo_url: str | None,
    ) -> Community:
        community.logo_url = logo_url
        await db.flush()
        await db.refresh(community)
        return community

    async def update_banner(
        self,
        db: AsyncSession,
        community: Community,
        banner_url: str | None,
    ) -> Community:
        community.banner_url = banner_url
        await db.flush()
        await db.refresh(community)
        return community

    async def update_bylaws(
        self,
        db: AsyncSession,
        community: Community,
        bylaws_url: str | None,
    ) -> Community:
        community.bylaws_url = bylaws_url
        await db.flush()
        await db.refresh(community)
        return community

    async def delete(self, db: AsyncSession, community: Community) -> None:
        community.soft_delete()
        await db.flush()

    async def get_user_communities(
        self,
        db: AsyncSession,
        account_id: UUID,
    ) -> list[Community]:
        result = await db.execute(
            select(Community)
            .join(CommunityMember)
            .where(
                CommunityMember.account_id == account_id,
                CommunityMember.status == MemberStatus.ACTIVE,
                Community.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())


community_service = CommunityService()
