from typing import Any


class AppException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(
        self,
        resource: str,
        identifier: str | None = None,
    ) -> None:
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(
            code="NOT_FOUND",
            message=message,
            status_code=404,
        )


class AlreadyExistsError(AppException):
    def __init__(
        self,
        resource: str,
        field: str,
        value: str,
    ) -> None:
        super().__init__(
            code="ALREADY_EXISTS",
            message=f"{resource} with {field} '{value}' already exists",
            status_code=409,
        )


class PermissionDeniedError(AppException):
    def __init__(
        self,
        message: str = "You don't have permission to perform this action",
    ) -> None:
        super().__init__(
            code="PERMISSION_DENIED",
            message=message,
            status_code=403,
        )


class ValidationError(AppException):
    def __init__(
        self,
        message: str,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=422,
            details=details,
        )


class RateLimitExceededError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message="Too many requests. Please try again later.",
            status_code=429,
        )


class ServiceUnavailableError(AppException):
    def __init__(
        self,
        service: str,
        message: str | None = None,
    ) -> None:
        super().__init__(
            code="SERVICE_UNAVAILABLE",
            message=message or f"{service} is currently unavailable",
            status_code=503,
        )
