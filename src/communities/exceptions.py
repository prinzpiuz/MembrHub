from src.core.exceptions import AlreadyExistsError, AppException, NotFoundError


class CommunityNotFoundError(NotFoundError):
    def __init__(self, identifier: str | None = None) -> None:
        super().__init__(resource="Community", identifier=identifier)


class CommunitySlugExistsError(AlreadyExistsError):
    def __init__(self, slug: str) -> None:
        super().__init__(resource="Community", field="slug", value=slug)


class CommunityNotActiveError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="COMMUNITY_NOT_ACTIVE",
            message="This community has been deactivated",
            status_code=403,
        )
