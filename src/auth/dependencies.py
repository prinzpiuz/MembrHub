from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.accounts.exceptions import AccountNotActiveError, AccountNotFoundError
from src.accounts.models import Account
from src.accounts.service import account_service
from src.auth.exceptions import InvalidTokenError, UnauthorizedError
from src.constants import TokenType
from src.core.database import DbSession
from src.core.security import verify_token


security = HTTPBearer(auto_error=False)


async def get_current_account(
    db: DbSession,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(security),
    ],
) -> Account:
    if credentials is None:
        raise UnauthorizedError()

    payload = verify_token(credentials.credentials, TokenType.ACCESS)
    if payload is None:
        raise InvalidTokenError()

    try:
        account_id = UUID(payload["sub"])
    except (ValueError, KeyError) as err:
        raise InvalidTokenError() from err

    try:
        account = await account_service.get_by_id(db, account_id)
    except AccountNotFoundError as err:
        raise InvalidTokenError() from err

    if not account.is_active:
        raise AccountNotActiveError()

    return account


async def get_current_account_optional(
    db: DbSession,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(security),
    ],
) -> Account | None:
    if credentials is None:
        return None

    payload = verify_token(credentials.credentials, TokenType.ACCESS)
    if payload is None:
        return None

    try:
        account_id = UUID(payload["sub"])
        account = await account_service.get_by_id(db, account_id)
        if not account.is_active:
            return None
        return account
    except (ValueError, AccountNotFoundError):
        return None


def get_device_info(
    request: Request,
    user_agent: Annotated[str | None, Header(alias="User-Agent")] = None,
) -> str | None:
    client_ip = request.client.host if request.client else "unknown"
    return f"{user_agent or 'unknown'} ({client_ip})"


CurrentAccount = Annotated[Account, Depends(get_current_account)]
CurrentAccountOptional = Annotated[
    Account | None, Depends(get_current_account_optional)
]
DeviceInfo = Annotated[str | None, Depends(get_device_info)]
