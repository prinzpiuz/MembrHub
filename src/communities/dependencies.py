from typing import Annotated

from fastapi import Depends, Path

from src.communities.exceptions import CommunityNotActiveError
from src.communities.models import Community
from src.communities.service import community_service
from src.core.database import DbSession


async def get_community_by_slug(
    db: DbSession,
    slug: Annotated[str, Path(description="Community slug")],
) -> Community:
    community = await community_service.get_by_slug(db, slug)
    if not community.is_active:
        raise CommunityNotActiveError()
    return community


CommunityBySlug = Annotated[Community, Depends(get_community_by_slug)]
