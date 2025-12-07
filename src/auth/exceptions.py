from src.core.exceptions import AppException


class InvalidCredentialsError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="INVALID_CREDENTIALS",
            message="Invalid email or password",
            status_code=401,
        )


class InvalidTokenError(AppException):
    def __init__(self, message: str = "Invalid or expired token") -> None:
        super().__init__(
            code="INVALID_TOKEN",
            message=message,
            status_code=401,
        )


class TokenExpiredError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="TOKEN_EXPIRED",
            message="Token has expired",
            status_code=401,
        )


class TokenRevokedError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="TOKEN_REVOKED",
            message="Token has been revoked",
            status_code=401,
        )


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=401,
        )
