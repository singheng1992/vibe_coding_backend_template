"""用户数据访问层。

提供用户相关的数据库操作。
"""

import uuid
from typing import Any

from sqlalchemy import Select, UnaryExpression, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.user import RefreshToken, User
from app.schemas.user import UserCreate, UserUpdate


class UserRepo(CRUDBase[User, UserCreate, UserUpdate]):
    """用户数据访问类。"""

    async def get_by_email(
        self,
        db: AsyncSession,
        *,
        email: str,
    ) -> User | None:
        """根据邮箱获取用户。

        Args:
            db: 数据库会话。
            email: 用户邮箱。

        Returns:
            用户实例，如果不存在则返回 None。
        """
        return await self.get_by(db, email=email)

    async def get_by_username(
        self,
        db: AsyncSession,
        *,
        username: str,
    ) -> User | None:
        """根据用户名获取用户。

        Args:
            db: 数据库会话。
            username: 用户名。

        Returns:
            用户实例，如果不存在则返回 None。
        """
        return await self.get_by(db, username=username)

    async def get_by_email_or_username(
        self,
        db: AsyncSession,
        *,
        email_or_username: str,
    ) -> User | None:
        """根据邮箱或用户名获取用户。

        Args:
            db: 数据库会话。
            email_or_username: 邮箱或用户名。

        Returns:
            用户实例，如果不存在则返回 None。
        """
        from sqlalchemy import or_

        statement = select(User).where(
            or_(User.email == email_or_username, User.username == email_or_username)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: UserCreate | dict[str, Any],
    ) -> User:
        """创建用户。

        Args:
            db: 数据库会话。
            obj_in: 创建数据。

        Returns:
            创建的用户实例。
        """
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.model_dump()

        # 密码哈希处理
        from app.core.security import get_password_hash

        if "password" in create_data:
            create_data["hashed_password"] = get_password_hash(create_data.pop("password"))

        return await super().create(db, obj_in=create_data)

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: User,
        obj_in: UserUpdate | dict[str, Any],
    ) -> User:
        """更新用户。

        Args:
            db: 数据库会话。
            db_obj: 要更新的用户实例。
            obj_in: 更新数据。

        Returns:
            更新后的用户实例。
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # 密码哈希处理
        if "password" in update_data and update_data["password"] is not None:
            from app.core.security import get_password_hash

            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: UnaryExpression[Any] | None = None,
    ) -> list[User]:
        """获取用户列表。

        Args:
            db: 数据库会话。
            skip: 跳过的记录数。
            limit: 返回的最大记录数。
            order_by: 排序条件。

        Returns:
            用户实例列表。
        """
        if order_by is None:
            order_by = desc(User.created_at)
        return list(await super().get_multi(db, skip=skip, limit=limit, order_by=order_by))


class RefreshTokenRepo(CRUDBase[RefreshToken, dict[str, Any], dict[str, Any]]):
    """刷新令牌数据访问类。"""

    async def get_by_token(
        self,
        db: AsyncSession,
        *,
        token: str,
    ) -> RefreshToken | None:
        """根据令牌字符串获取刷新令牌。

        Args:
            db: 数据库会话。
            token: 令牌字符串。

        Returns:
            刷新令牌实例，如果不存在则返回 None。
        """
        return await self.get_by(db, token=token)

    async def get_valid_by_token(
        self,
        db: AsyncSession,
        *,
        token: str,
    ) -> RefreshToken | None:
        """根据令牌字符串获取有效的刷新令牌。

        Args:
            db: 数据库会话。
            token: 令牌字符串。

        Returns:
            有效的刷新令牌实例，如果不存在或无效则返回 None。
        """
        refresh_token = await self.get_by_token(db, token=token)
        if refresh_token and refresh_token.is_valid:
            return refresh_token
        return None

    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        token: str,
        expires_at: Any,
    ) -> RefreshToken:
        """创建刷新令牌。

        Args:
            db: 数据库会话。
            user_id: 用户 ID。
            token: 令牌字符串。
            expires_at: 过期时间。

        Returns:
            创建的刷新令牌实例。
        """
        return await super().create(
            db,
            obj_in={
                "user_id": user_id,
                "token": token,
                "expires_at": expires_at,
            },
        )

    async def revoke(
        self,
        db: AsyncSession,
        *,
        token: str,
    ) -> RefreshToken | None:
        """撤回刷新令牌。

        Args:
            db: 数据库会话。
            token: 令牌字符串。

        Returns:
            被撤回的刷新令牌实例，如果不存在则返回 None。
        """
        refresh_token = await self.get_by_token(db, token=token)
        if refresh_token:
            refresh_token.revoke()
            await db.flush()
            await db.refresh(refresh_token)
        return refresh_token

    async def revoke_user_tokens(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
    ) -> list[RefreshToken]:
        """撤回用户的所有刷新令牌。

        Args:
            db: 数据库会话。
            user_id: 用户 ID。

        Returns:
            被撤回的刷新令牌实例列表。
        """
        from sqlalchemy import select

        statement = select(RefreshToken).where(
            RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None)
        )
        result = await db.execute(statement)
        tokens = list(result.scalars().all())

        for token in tokens:
            token.revoke()

        await db.flush()
        return tokens

    async def delete_expired(
        self,
        db: AsyncSession,
    ) -> int:
        """删除过期的刷新令牌。

        Args:
            db: 数据库会话。

        Returns:
            删除的记录数。
        """
        from datetime import datetime, timezone
        from sqlalchemy import delete

        statement = delete(RefreshToken).where(
            RefreshToken.expires_at < datetime.now(timezone.utc)
        )
        result = await db.execute(statement)
        await db.flush()
        return result.rowcount


# 创建实例
user_repo = UserRepo(User)
refresh_token_repo = RefreshTokenRepo(RefreshToken)
