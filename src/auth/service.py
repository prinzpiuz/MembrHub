from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.accounts.exceptions import AccountNotActiveError, EmailAlreadyExistsError
from src.accounts.models import Account
from src.accounts.service import account_service
from src.auth.config import auth_config
from src.auth.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
    TokenRevokedError,
)
from src.auth.models import RefreshToken
from src.auth.schemas import RegisterRequest, TokenResponse
from src.constants import TokenType
from src.core.security import (
    create_token,
    generate_secure_token,
    hash_token,
    verify_password,
    verify_token,
)


class AuthService:
    async def register(
        self,
        db: AsyncSession,
        data: RegisterRequest,
    ) -> Account:
        existing = await account_service.get_by_email(db, data.email)
        if existing:
            raise EmailAlreadyExistsError(data.email)

        account = await account_service.create(
            db=db,
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
        )
        return account

    async def authenticate(
        self,
        db: AsyncSession,
        email: str,
        password: str,
        device_info: str | None = None,
    ) -> TokenResponse:
        account = await account_service.get_by_email(db, email)
        if account is None:
            raise InvalidCredentialsError()

        if not verify_password(password, account.hashed_password):
            raise InvalidCredentialsError()

        if not account.is_active:
            raise AccountNotActiveError()

        await account_service.update_last_login(db, account)

        access_token = create_token(
            subject=account.id,
            token_type=TokenType.ACCESS,
        )

        refresh_token = generate_secure_token()
        refresh_token_hash = hash_token(refresh_token)

        expires_at = datetime.now(UTC) + timedelta(
            days=auth_config.REFRESH_TOKEN_EXPIRE_DAYS
        )

        db_refresh_token = RefreshToken(
            account_id=account.id,
            token_hash=refresh_token_hash,
            device_info=device_info,
            expires_at=expires_at,
        )
        db.add(db_refresh_token)
        await db.flush()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh_tokens(
        self,
        db: AsyncSession,
        refresh_token: str,
        device_info: str | None = None,
    ) -> TokenResponse:
        token_hash = hash_token(refresh_token)

        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        db_token = result.scalar_one_or_none()

        if db_token is None:
            raise InvalidTokenError("Invalid refresh token")

        if db_token.is_revoked:
            raise TokenRevokedError()

        if db_token.is_expired:
            raise TokenExpiredError()

        account = db_token.account
        if not account.is_active:
            raise AccountNotActiveError()

        db_token.revoked_at = datetime.now(UTC)

        access_token = create_token(
            subject=account.id,
            token_type=TokenType.ACCESS,
        )

        new_refresh_token = generate_secure_token()
        new_refresh_token_hash = hash_token(new_refresh_token)

        expires_at = datetime.now(UTC) + timedelta(
            days=auth_config.REFRESH_TOKEN_EXPIRE_DAYS
        )

        new_db_refresh_token = RefreshToken(
            account_id=account.id,
            token_hash=new_refresh_token_hash,
            device_info=device_info,
            expires_at=expires_at,
        )
        db.add(new_db_refresh_token)
        await db.flush()

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

    async def logout(
        self,
        db: AsyncSession,
        refresh_token: str,
    ) -> bool:
        token_hash = hash_token(refresh_token)

        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        db_token = result.scalar_one_or_none()

        if db_token is not None and not db_token.is_revoked:
            db_token.revoked_at = datetime.now(UTC)
            await db.flush()

        return True

    async def logout_all_devices(
        self,
        db: AsyncSession,
        account_id: UUID,
    ) -> int:
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.account_id == account_id,
                RefreshToken.revoked_at.is_(None),
            )
        )
        tokens = result.scalars().all()

        now = datetime.now(UTC)
        for token in tokens:
            token.revoked_at = now

        await db.flush()
        return len(tokens)

    async def request_password_reset(
        self,
        db: AsyncSession,
        email: str,
    ) -> str | None:
        account = await account_service.get_by_email(db, email)
        if account is None:
            return None

        token = create_token(
            subject=account.id,
            token_type=TokenType.PASSWORD_RESET,
        )
        return token

    async def reset_password(
        self,
        db: AsyncSession,
        token: str,
        new_password: str,
    ) -> Account:
        payload = verify_token(token, TokenType.PASSWORD_RESET)
        if payload is None:
            raise InvalidTokenError("Invalid or expired password reset token")

        account_id = UUID(payload["sub"])
        account = await account_service.get_by_id(db, account_id)

        await account_service.set_password(db, account, new_password)

        await self.logout_all_devices(db, account.id)

        return account

    async def request_email_verification(
        self,
        _: AsyncSession,
        account: Account,
    ) -> str:
        token = create_token(
            subject=account.id,
            token_type=TokenType.EMAIL_VERIFICATION,
        )
        return token

    async def verify_email(
        self,
        db: AsyncSession,
        token: str,
    ) -> Account:
        payload = verify_token(token, TokenType.EMAIL_VERIFICATION)
        if payload is None:
            raise InvalidTokenError("Invalid or expired verification token")

        account_id = UUID(payload["sub"])
        account = await account_service.get_by_id(db, account_id)

        await account_service.verify_email(db, account)
        return account


auth_service = AuthService()
