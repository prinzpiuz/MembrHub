from fastapi import APIRouter, BackgroundTasks, status

from src.accounts.schemas import AccountResponse
from src.auth.dependencies import CurrentAccount, DeviceInfo
from src.auth.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from src.auth.service import auth_service
from src.aws.ses import ses_service
from src.core.config import settings
from src.core.database import DbSession
from src.core.schemas import MessageResponse


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    db: DbSession,
    data: RegisterRequest,
) -> AccountResponse:
    account = await auth_service.register(db, data)
    return AccountResponse.model_validate(account)


@router.post("/login", response_model=TokenResponse)
async def login(
    db: DbSession,
    data: LoginRequest,
    device_info: DeviceInfo,
) -> TokenResponse:
    return await auth_service.authenticate(
        db=db,
        email=data.email,
        password=data.password,
        device_info=device_info,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    db: DbSession,
    data: RefreshTokenRequest,
) -> MessageResponse:
    await auth_service.logout(db, data.refresh_token)
    return MessageResponse(message="Successfully logged out")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    db: DbSession,
    data: RefreshTokenRequest,
    device_info: DeviceInfo,
) -> TokenResponse:
    return await auth_service.refresh_tokens(
        db=db,
        refresh_token=data.refresh_token,
        device_info=device_info,
    )


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    db: DbSession,
    data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
) -> MessageResponse:
    token = await auth_service.request_password_reset(db, data.email)

    if token:
        reset_link = f"{settings.CORS_ORIGINS[0]}/reset-password?token={token}"
        background_tasks.add_task(
            ses_service.send_password_reset_email,
            to_email=data.email,
            reset_link=reset_link,
        )

    return MessageResponse(
        message="If an account with this email exists, a password reset link has been sent"
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    db: DbSession,
    data: ResetPasswordRequest,
) -> MessageResponse:
    await auth_service.reset_password(db, data.token, data.new_password)
    return MessageResponse(message="Password has been reset successfully")


@router.get("/me", response_model=AccountResponse)
async def get_current_user(
    current_account: CurrentAccount,
) -> AccountResponse:
    return AccountResponse.model_validate(current_account)
