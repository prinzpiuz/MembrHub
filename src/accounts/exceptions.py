from src.core.exceptions import AlreadyExistsError, AppException, NotFoundError


class AccountNotFoundError(NotFoundError):
    def __init__(self, identifier: str | None = None) -> None:
        super().__init__(resource="Account", identifier=identifier)


class EmailAlreadyExistsError(AlreadyExistsError):
    def __init__(self, email: str) -> None:
        super().__init__(resource="Account", field="email", value=email)


class AccountNotActiveError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="ACCOUNT_NOT_ACTIVE",
            message="This account has been deactivated",
            status_code=403,
        )


class InvalidPasswordError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="INVALID_PASSWORD",
            message="Current password is incorrect",
            status_code=400,
        )
