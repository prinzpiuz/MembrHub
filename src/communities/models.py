from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from src.constants import CommunityType, CommunityVisibility
from src.core.models import Base, SoftDeleteMixin, TimestampMixin


if TYPE_CHECKING:
    from src.accounts.models import Account
    from src.membership.models import CommunityInvitation, CommunityMember


class Community(Base, TimestampMixin, SoftDeleteMixin):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return "communities"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    type: Mapped[CommunityType] = mapped_column(
        String(50),
        default=CommunityType.OTHER,
        nullable=False,
    )
    visibility: Mapped[CommunityVisibility] = mapped_column(
        String(50),
        default=CommunityVisibility.PRIVATE,
        nullable=False,
    )

    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    registration_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bylaws_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    banner_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    settings: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )

    created_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    creator: Mapped[Account] = relationship("Account", lazy="selectin")
    members: Mapped[list[CommunityMember]] = relationship(
        "CommunityMember",
        back_populates="community",
        lazy="selectin",
    )
    invitations: Mapped[list[CommunityInvitation]] = relationship(
        "CommunityInvitation",
        back_populates="community",
        lazy="selectin",
    )

    @property
    def member_count(self) -> int:
        return len([m for m in self.members if m.status == "active"])

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        self.settings[key] = value
