from typing import Annotated
from uuid import UUID

from fastapi import Depends, Path

from src.accounts.models import Account
from src.accounts.service import account_service
from src.core.database import DbSession


async def get_account_by_id(
    db: DbSession,
    account_id: Annotated[UUID, Path(description="Account ID")],
) -> Account:
    return await account_service.get_by_id(db, account_id)


AccountById = Annotated[Account, Depends(get_account_by_id)]
