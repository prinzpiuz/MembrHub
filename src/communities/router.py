from typing import Annotated

from fastapi import APIRouter, File, UploadFile, status

from src.auth.dependencies import CurrentAccount
from src.aws.s3 import s3_service
from src.communities.dependencies import CommunityBySlug
from src.communities.schemas import (
    CommunityCreate,
    CommunityResponse,
    CommunitySettingsUpdate,
    CommunityUpdate,
)
from src.communities.service import community_service
from src.core.database import DbSession
from src.core.schemas import MessageResponse
from src.membership.dependencies import RequireOwner


router = APIRouter(prefix="/communities", tags=["Communities"])


@router.post(
    "",
    response_model=CommunityResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_community(
    db: DbSession,
    current_account: CurrentAccount,
    data: CommunityCreate,
) -> CommunityResponse:
    community = await community_service.create(
        db=db,
        data=data,
        created_by=current_account.id,
    )
    return CommunityResponse.model_validate(community)


@router.get("", response_model=list[CommunityResponse])
async def list_my_communities(
    db: DbSession,
    current_account: CurrentAccount,
) -> list[CommunityResponse]:
    communities = await community_service.get_user_communities(db, current_account.id)
    return [CommunityResponse.model_validate(c) for c in communities]


@router.get("/{slug}", response_model=CommunityResponse)
async def get_community(
    community: CommunityBySlug,
) -> CommunityResponse:
    return CommunityResponse.model_validate(community)


@router.patch("/{slug}", response_model=CommunityResponse)
async def update_community(
    db: DbSession,
    community: CommunityBySlug,
    data: CommunityUpdate,
    _: RequireOwner,
) -> CommunityResponse:
    community = await community_service.update(db, community, data)
    return CommunityResponse.model_validate(community)


@router.delete("/{slug}", response_model=MessageResponse)
async def delete_community(
    db: DbSession,
    community: CommunityBySlug,
    _: RequireOwner,
) -> MessageResponse:
    await community_service.delete(db, community)
    return MessageResponse(message="Community deleted successfully")


@router.patch("/{slug}/settings", response_model=CommunityResponse)
async def update_community_settings(
    db: DbSession,
    community: CommunityBySlug,
    data: CommunitySettingsUpdate,
    _: RequireOwner,
) -> CommunityResponse:
    community = await community_service.update_settings(db, community, data)
    return CommunityResponse.model_validate(community)


@router.post("/{slug}/logo", response_model=CommunityResponse)
async def upload_logo(
    db: DbSession,
    community: CommunityBySlug,
    file: Annotated[UploadFile, File(description="Logo image")],
    _: RequireOwner,
) -> CommunityResponse:
    content = await file.read()
    logo_url = await s3_service.upload_file(
        file_content=content,
        filename=file.filename or "logo.jpg",
        folder="logos",
        community_id=community.id,
        content_type=file.content_type,
    )
    community = await community_service.update_logo(db, community, logo_url)
    return CommunityResponse.model_validate(community)


@router.delete("/{slug}/logo", response_model=CommunityResponse)
async def delete_logo(
    db: DbSession,
    community: CommunityBySlug,
    _: RequireOwner,
) -> CommunityResponse:
    if community.logo_url:
        await s3_service.delete_file(community.logo_url)
    community = await community_service.update_logo(db, community, None)
    return CommunityResponse.model_validate(community)


@router.post("/{slug}/banner", response_model=CommunityResponse)
async def upload_banner(
    db: DbSession,
    community: CommunityBySlug,
    file: Annotated[UploadFile, File(description="Banner image")],
    _: RequireOwner,
) -> CommunityResponse:
    content = await file.read()
    banner_url = await s3_service.upload_file(
        file_content=content,
        filename=file.filename or "banner.jpg",
        folder="banners",
        community_id=community.id,
        content_type=file.content_type,
    )
    community = await community_service.update_banner(db, community, banner_url)
    return CommunityResponse.model_validate(community)


@router.delete("/{slug}/banner", response_model=CommunityResponse)
async def delete_banner(
    db: DbSession,
    community: CommunityBySlug,
    _: RequireOwner,
) -> CommunityResponse:
    if community.banner_url:
        await s3_service.delete_file(community.banner_url)
    community = await community_service.update_banner(db, community, None)
    return CommunityResponse.model_validate(community)


@router.post("/{slug}/bylaws", response_model=CommunityResponse)
async def upload_bylaws(
    db: DbSession,
    community: CommunityBySlug,
    file: Annotated[UploadFile, File(description="Bylaws document (PDF)")],
    _: RequireOwner,
) -> CommunityResponse:
    content = await file.read()
    bylaws_url = await s3_service.upload_file(
        file_content=content,
        filename=file.filename or "bylaws.pdf",
        folder="bylaws",
        community_id=community.id,
        content_type=file.content_type,
    )
    community = await community_service.update_bylaws(db, community, bylaws_url)
    return CommunityResponse.model_validate(community)


@router.delete("/{slug}/bylaws", response_model=CommunityResponse)
async def delete_bylaws(
    db: DbSession,
    community: CommunityBySlug,
    _: RequireOwner,
) -> CommunityResponse:
    if community.bylaws_url:
        await s3_service.delete_file(community.bylaws_url)
    community = await community_service.update_bylaws(db, community, None)
    return CommunityResponse.model_validate(community)
