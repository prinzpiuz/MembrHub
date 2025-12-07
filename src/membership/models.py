from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from src.constants import MemberRole, MemberStatus
from src.core.models import Base, TimestampMixin


if TYPE_CHECKING:
    from src.accounts.models import Account
    from src.communities.models import Community


class CommunityMember(Base, TimestampMixin):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return "community_members"

    __table_args__ = (
        UniqueConstraint("community_id", "account_id", name="uq_community_member"),
    )

    community_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("communities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[MemberRole] = mapped_column(
        String(50),
        default=MemberRole.MEMBER,
        nullable=False,
    )
    status: Mapped[MemberStatus] = mapped_column(
        String(50),
        default=MemberStatus.PENDING,
        nullable=False,
    )
    is_committee_member: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    invited_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("community_members.id", ondelete="SET NULL"),
        nullable=True,
    )
    joined_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    community: Mapped[Community] = relationship(
        "Community",
        back_populates="members",
        lazy="selectin",
    )
    account: Mapped[Account] = relationship(
        "Account",
        back_populates="memberships",
        lazy="selectin",
    )
    inviter: Mapped[CommunityMember | None] = relationship(
        "CommunityMember",
        remote_side="CommunityMember.id",
        lazy="selectin",
    )

    @property
    def is_owner(self) -> bool:
        return self.role == MemberRole.OWNER

    @property
    def is_admin(self) -> bool:
        return self.role in (MemberRole.OWNER, MemberRole.ADMIN)

    @property
    def is_moderator(self) -> bool:
        return self.role in (MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MODERATOR)

    @property
    def is_active(self) -> bool:
        return self.status == MemberStatus.ACTIVE


class CommunityInvitation(Base, TimestampMixin):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return "community_invitations"

    community_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("communities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    role: Mapped[MemberRole] = mapped_column(
        String(50),
        default=MemberRole.MEMBER,
        nullable=False,
    )
    is_committee_member: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    invited_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("community_members.id", ondelete="CASCADE"),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    community: Mapped[Community] = relationship(
        "Community",
        back_populates="invitations",
        lazy="selectin",
    )
    inviter_member: Mapped[CommunityMember] = relationship(
        "CommunityMember",
        lazy="selectin",
    )

    @property
    def is_accepted(self) -> bool:
        return self.accepted_at is not None

    @property
    def is_expired(self) -> bool:
        return datetime.now(UTC) > self.expires_at

    @property
    def is_valid(self) -> bool:
        return not self.is_accepted and not self.is_expired
