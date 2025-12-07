from src.core.exceptions import ServiceUnavailableError


class EmailSendError(ServiceUnavailableError):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            service="Email Service",
            message=message or "Failed to send email",
        )


class FileUploadError(ServiceUnavailableError):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            service="File Storage",
            message=message or "Failed to upload file",
        )


class FileDeleteError(ServiceUnavailableError):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            service="File Storage",
            message=message or "Failed to delete file",
        )
