from enum import StrEnum


class Environment(StrEnum):
    LOCAL = "LOCAL"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"
    TESTING = "TESTING"


class CommunityType(StrEnum):
    FAMILY = "family"
    CHURCH = "church"
    ORGANIZATION = "organization"
    SURNAME = "surname"
    OTHER = "other"


class CommunityVisibility(StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"
    INVITE_ONLY = "invite_only"


class MemberRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MODERATOR = "moderator"
    MEMBER = "member"


class MemberStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
    PASSWORD_RESET = "password_reset"  # noqa: S105
    EMAIL_VERIFICATION = "email_verification"
    INVITATION = "invitation"
