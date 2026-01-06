"""数据库模型基础类。

定义所有模型的基类和 Mixin。
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """数据库模型基类。

    所有 SQLAlchemy 模型的基类，提供通用功能。
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """自动生成表名。

        将类名转换为蛇形复数形式作为表名。

        Returns:
            表名字符串。
        """
        name = cls.__name__
        # 转换为蛇形命名
        result = [name[0].lower()]
        for char in name[1:]:
            if char.isupper():
                result.extend(["_", char.lower()])
            else:
                result.append(char)
        table_name = "".join(result)
        # 添加复数 s
        return f"{table_name}s"

    def __repr__(self) -> str:
        """返回模型的字符串表示。

        Returns:
            模型的字符串表示。
        """
        class_name = self.__class__.__name__
        attrs = []
        for key in self.__mapper__.columns.keys():
            value = getattr(self, key, None)
            if key == "hashed_password":
                value = "***"
            attrs.append(f"{key}={value!r}")
        return f"{class_name}({', '.join(attrs)})"


class UUIDMixin:
    """UUID 主键 Mixin。

    为模型提供 UUID 主键。
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )


class TimestampMixin:
    """时间戳 Mixin。

    为模型提供创建时间和更新时间字段。
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class SoftDeleteMixin:
    """软删除 Mixin。

    为模型提供软删除功能。
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        nullable=True,
        index=True,
    )

    @property
    def is_deleted(self) -> bool:
        """检查是否已删除。

        Returns:
            是否已删除。
        """
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """软删除记录。"""
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        """恢复已删除的记录。"""
        self.deleted_at = None
