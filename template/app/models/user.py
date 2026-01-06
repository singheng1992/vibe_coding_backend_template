"""用户模型。

定义用户和刷新令牌的数据模型。
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """用户模型。

    存储用户认证和基本信息。
    """

    # 用户认证信息
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # 用户基本信息
    full_name: Mapped[str | None] = mapped_column(
        String(100),
        default=None,
        nullable=True,
    )

    # 用户状态
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )


class RefreshToken(Base, UUIDMixin):
    """刷新令牌模型。

    管理 JWT 刷新令牌的存储和撤回。
    """

    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        index=True,
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        nullable=True,
    )

    @property
    def is_revoked(self) -> bool:
        """检查令牌是否已撤回。

        Returns:
            令牌是否已撤回。
        """
        return self.revoked_at is not None

    @property
    def is_expired(self) -> bool:
        """检查令牌是否已过期。

        Returns:
            令牌是否已过期。
        """
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_valid(self) -> bool:
        """检查令牌是否有效。

        Returns:
            令牌是否有效（未撤回且未过期）。
        """
        return not self.is_revoked and not self.is_expired

    def revoke(self) -> None:
        """撤回令牌。"""
        self.revoked_at = datetime.now(timezone.utc)
