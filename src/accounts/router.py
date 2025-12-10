from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from src.accounts.schemas import AccountResponse, PasswordChange, ProfileUpdate
from src.accounts.service import account_service
from src.auth.dependencies import CurrentAccount
from src.aws.s3 import s3_service
from src.core.database import DbSession
from src.core.schemas import MessageResponse


router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get("/me", response_model=AccountResponse)
async def get_current_account(
    current_account: CurrentAccount,
) -> AccountResponse:
    return AccountResponse.model_validate(current_account)


@router.patch("/me", response_model=AccountResponse)
async def update_profile(
    db: DbSession,
    current_account: CurrentAccount,
    data: ProfileUpdate,
) -> AccountResponse:
    account = await account_service.update_profile(db, current_account, data)
    return AccountResponse.model_validate(account)


@router.patch("/me/password", response_model=MessageResponse)
async def change_password(
    db: DbSession,
    current_account: CurrentAccount,
    data: PasswordChange,
) -> MessageResponse:
    await account_service.change_password(db, current_account, data)
    return MessageResponse(message="Password changed successfully")


@router.post("/me/avatar", response_model=AccountResponse)
async def upload_avatar(
    db: DbSession,
    current_account: CurrentAccount,
    file: Annotated[UploadFile, File(description="Avatar image")],
) -> AccountResponse:
    content = await file.read()
    avatar_url = await s3_service.upload_file(
        file_content=content,
        filename=file.filename or "avatar.jpg",
        folder="avatars",
        content_type=file.content_type,
    )
    account = await account_service.update_avatar(db, current_account, avatar_url)
    return AccountResponse.model_validate(account)


@router.delete("/me/avatar", response_model=AccountResponse)
async def delete_avatar(
    db: DbSession,
    current_account: CurrentAccount,
) -> AccountResponse:
    if current_account.avatar_url:
        await s3_service.delete_file(current_account.avatar_url)
    account = await account_service.update_avatar(db, current_account, "")
    return AccountResponse.model_validate(account)
