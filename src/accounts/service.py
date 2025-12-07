from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.accounts.exceptions import (
    AccountNotFoundError,
    EmailAlreadyExistsError,
    InvalidPasswordError,
)
from src.accounts.models import Account
from src.accounts.schemas import PasswordChange, ProfileUpdate
from src.core.security import hash_password, verify_password


class AccountService:
    async def get_by_id(self, db: AsyncSession, account_id: UUID) -> Account:
        result = await db.execute(select(Account).where(Account.id == account_id))
        account = result.scalar_one_or_none()
        if account is None:
            raise AccountNotFoundError(str(account_id))
        return account

    async def get_by_email(self, db: AsyncSession, email: str) -> Account | None:
        result = await db.execute(select(Account).where(Account.email == email.lower()))
        return result.scalar_one_or_none()

    async def get_by_email_or_raise(self, db: AsyncSession, email: str) -> Account:
        account = await self.get_by_email(db, email)
        if account is None:
            raise AccountNotFoundError(email)
        return account

    async def create(
        self,
        db: AsyncSession,
        email: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> Account:
        existing = await self.get_by_email(db, email)
        if existing:
            raise EmailAlreadyExistsError(email)

        account = Account(
            email=email.lower(),
            hashed_password=hash_password(password),
            first_name=first_name,
            last_name=last_name,
        )
        db.add(account)
        await db.flush()
        await db.refresh(account)
        return account

    async def update_profile(
        self,
        db: AsyncSession,
        account: Account,
        data: ProfileUpdate,
    ) -> Account:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(account, field, value)

        await db.flush()
        await db.refresh(account)
        return account

    async def update_avatar(
        self,
        db: AsyncSession,
        account: Account,
        avatar_url: str,
    ) -> Account:
        account.avatar_url = avatar_url
        await db.flush()
        await db.refresh(account)
        return account

    async def change_password(
        self,
        db: AsyncSession,
        account: Account,
        data: PasswordChange,
    ) -> Account:
        if not verify_password(data.current_password, account.hashed_password):
            raise InvalidPasswordError()

        account.hashed_password = hash_password(data.new_password)
        await db.flush()
        await db.refresh(account)
        return account

    async def set_password(
        self,
        db: AsyncSession,
        account: Account,
        new_password: str,
    ) -> Account:
        account.hashed_password = hash_password(new_password)
        await db.flush()
        await db.refresh(account)
        return account

    async def verify_email(self, db: AsyncSession, account: Account) -> Account:
        account.is_verified = True
        await db.flush()
        await db.refresh(account)
        return account

    async def update_last_login(self, db: AsyncSession, account: Account) -> Account:
        account.last_login_at = datetime.now(UTC)
        await db.flush()
        await db.refresh(account)
        return account

    async def deactivate(self, db: AsyncSession, account: Account) -> Account:
        account.is_active = False
        await db.flush()
        await db.refresh(account)
        return account

    async def activate(self, db: AsyncSession, account: Account) -> Account:
        account.is_active = True
        await db.flush()
        await db.refresh(account)
        return account


account_service = AccountService()
