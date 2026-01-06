"""用户服务模块。

提供用户管理相关的业务逻辑。
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user_repo import user_repo
from app.exceptions import BusinessException, ResourceNotFoundException
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.base import PageResponse


class UserService:
    """用户服务类。"""

    @staticmethod
    async def get_user(
        db: AsyncSession,
        *,
        user_id: str,
    ) -> User:
        """获取用户信息。

        Args:
            db: 数据库会话。
            user_id: 用户 ID。

        Returns:
            用户实例。

        Raises:
            ResourceNotFoundException: 如果用户不存在。
        """
        user = await user_repo.get(db, id=user_id)
        if not user:
            raise ResourceNotFoundException(message="用户不存在")
        return user

    @staticmethod
    async def get_user_me(
        db: AsyncSession,
        *,
        current_user: User,
    ) -> User:
        """获取当前用户信息。

        Args:
            db: 数据库会话。
            current_user: 当前用户实例。

        Returns:
            当前用户实例。
        """
        return current_user

    @staticmethod
    async def update_user_me(
        db: AsyncSession,
        *,
        current_user: User,
        user_in: UserUpdate,
    ) -> User:
        """更新当前用户信息。

        Args:
            db: 数据库会话。
            current_user: 当前用户实例。
            user_in: 更新数据。

        Returns:
            更新后的用户实例。

        Raises:
            BusinessException: 如果邮箱已被其他用户使用。
        """
        # 如果要更新邮箱，检查是否已被使用
        if user_in.email and user_in.email != current_user.email:
            existing_user = await user_repo.get_by_email(db, email=user_in.email)
            if existing_user and existing_user.id != current_user.id:
                raise BusinessException(message="邮箱已被使用")

        return await user_repo.update(db, db_obj=current_user, obj_in=user_in)

    @staticmethod
    async def update_user(
        db: AsyncSession,
        *,
        user_id: str,
        user_in: UserUpdate,
    ) -> User:
        """更新用户信息。

        Args:
            db: 数据库会话。
            user_id: 用户 ID。
            user_in: 更新数据。

        Returns:
            更新后的用户实例。

        Raises:
            ResourceNotFoundException: 如果用户不存在。
            BusinessException: 如果邮箱已被其他用户使用。
        """
        user = await user_repo.get(db, id=user_id)
        if not user:
            raise ResourceNotFoundException(message="用户不存在")

        # 如果要更新邮箱，检查是否已被使用
        if user_in.email and user_in.email != user.email:
            existing_user = await user_repo.get_by_email(db, email=user_in.email)
            if existing_user and existing_user.id != user.id:
                raise BusinessException(message="邮箱已被使用")

        return await user_repo.update(db, db_obj=user, obj_in=user_in)

    @staticmethod
    async def delete_user(
        db: AsyncSession,
        *,
        user_id: str,
    ) -> None:
        """删除用户（软删除）。

        Args:
            db: 数据库会话。
            user_id: 用户 ID。

        Raises:
            ResourceNotFoundException: 如果用户不存在。
        """
        user = await user_repo.get(db, id=user_id)
        if not user:
            raise ResourceNotFoundException(message="用户不存在")

        user.soft_delete()
        await db.flush()

    @staticmethod
    async def get_users(
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 20,
    ) -> PageResponse:
        """获取用户列表。

        Args:
            db: 数据库会话。
            skip: 跳过的记录数。
            limit: 返回的最大记录数。

        Returns:
            分页响应。
        """
        users = await user_repo.get_multi(db, skip=skip, limit=limit)
        total = await user_repo.count(db)

        # 计算当前页码
        page = skip // limit + 1 if limit > 0 else 1

        return PageResponse.create(
            items=users,
            total=total,
            page=page,
            size=limit,
        )
