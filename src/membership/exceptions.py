from src.core.exceptions import (
    AlreadyExistsError,
    AppException,
    NotFoundError,
    PermissionDeniedError,
)


class MemberNotFoundError(NotFoundError):
    def __init__(self, identifier: str | None = None) -> None:
        super().__init__(resource="Member", identifier=identifier)


class InvitationNotFoundError(NotFoundError):
    def __init__(self, identifier: str | None = None) -> None:
        super().__init__(resource="Invitation", identifier=identifier)


class AlreadyMemberError(AlreadyExistsError):
    def __init__(self, email: str) -> None:
        super().__init__(resource="Member", field="email", value=email)


class InvitationAlreadyExistsError(AlreadyExistsError):
    def __init__(self, email: str) -> None:
        super().__init__(resource="Invitation", field="email", value=email)


class InvitationExpiredError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="INVITATION_EXPIRED",
            message="This invitation has expired",
            status_code=400,
        )


class InvitationAlreadyAcceptedError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="INVITATION_ALREADY_ACCEPTED",
            message="This invitation has already been accepted",
            status_code=400,
        )


class NotAMemberError(PermissionDeniedError):
    def __init__(self) -> None:
        super().__init__(message="You are not a member of this community")


class NotAnAdminError(PermissionDeniedError):
    def __init__(self) -> None:
        super().__init__(message="Only admins can perform this action")


class NotOwnerError(PermissionDeniedError):
    def __init__(self) -> None:
        super().__init__(message="Only the owner can perform this action")


class MaxAdminsReachedError(AppException):
    def __init__(self, max_admins: int) -> None:
        super().__init__(
            code="MAX_ADMINS_REACHED",
            message=f"This community can have a maximum of {max_admins} admins",
            status_code=400,
        )


class MaxCommitteeMembersReachedError(AppException):
    def __init__(self, max_members: int) -> None:
        super().__init__(
            code="MAX_COMMITTEE_MEMBERS_REACHED",
            message=f"This community can have a maximum of {max_members} committee members",
            status_code=400,
        )


class CannotRemoveOwnerError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="CANNOT_REMOVE_OWNER",
            message="The owner cannot be removed from the community",
            status_code=400,
        )


class CannotChangeOwnerRoleError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="CANNOT_CHANGE_OWNER_ROLE",
            message="The owner's role cannot be changed",
            status_code=400,
        )
