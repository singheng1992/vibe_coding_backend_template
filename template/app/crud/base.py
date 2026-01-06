"""基础 CRUD 模块。

定义通用的数据库操作基类。
"""

import uuid
from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import Select, UnaryExpression, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """基础 CRUD 类。

    提供通用的数据库操作方法。

    Attributes:
        model: SQLAlchemy 模型类。
    """

    def __init__(self, model: type[ModelType]) -> None:
        """初始化 CRUD 基类。

        Args:
            model: SQLAlchemy 模型类。
        """
        self.model = model

    async def get(
        self,
        db: AsyncSession,
        id: uuid.UUID,
    ) -> ModelType | None:
        """根据 ID 获取单个记录。

        Args:
            db: 数据库会话。
            id: 记录 ID。

        Returns:
            模型实例，如果不存在则返回 None。
        """
        statement = select(self.model).where(self.model.id == id)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def get_by(
        self,
        db: AsyncSession,
        **kwargs: Any,
    ) -> ModelType | None:
        """根据指定条件获取单个记录。

        Args:
            db: 数据库会话。
            **kwargs: 查询条件。

        Returns:
            模型实例，如果不存在则返回 None。

        Examples:
            ```python
            user = await user_repo.get_by(db, email="user@example.com")
            ```
        """
        statement = select(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                statement = statement.where(getattr(self.model, key) == value)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: UnaryExpression[Any] | None = None,
    ) -> Sequence[ModelType]:
        """获取多个记录。

        Args:
            db: 数据库会话。
            skip: 跳过的记录数。
            limit: 返回的最大记录数。
            order_by: 排序条件。

        Returns:
            模型实例列表。
        """
        statement = select(self.model)
        if order_by is not None:
            statement = statement.order_by(order_by)
        statement = statement.offset(skip).limit(limit)
        result = await db.execute(statement)
        return result.scalars().all()

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: CreateSchemaType | dict[str, Any],
    ) -> ModelType:
        """创建新记录。

        Args:
            db: 数据库会话。
            obj_in: 创建数据，可以是 Pydantic 模型或字典。

        Returns:
            创建的模型实例。
        """
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.model_dump()

        db_obj = self.model(**create_data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        """更新记录。

        Args:
            db: 数据库会话。
            db_obj: 要更新的数据库模型实例。
            obj_in: 更新数据，可以是 Pydantic 模型或字典。

        Returns:
            更新后的模型实例。
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(
        self,
        db: AsyncSession,
        *,
        id: uuid.UUID,
    ) -> ModelType | None:
        """删除记录。

        Args:
            db: 数据库会话。
            id: 要删除的记录 ID。

        Returns:
            被删除的模型实例，如果不存在则返回 None。
        """
        obj = await self.get(db, id)
        if obj is None:
            return None
        await db.delete(obj)
        await db.flush()
        return obj

    async def count(
        self,
        db: AsyncSession,
        *,
        statement: Select[tuple[ModelType]] | None = None,
    ) -> int:
        """统计记录数。

        Args:
            db: 数据库会话。
            statement: 查询语句，如果为 None 则统计所有记录。

        Returns:
            记录数。
        """
        if statement is None:
            statement = select(self.model)
        from sqlalchemy import func

        count_statement = select(func.count()).select_from(statement)
        result = await db.execute(count_statement)
        return result.scalar_one() or 0
