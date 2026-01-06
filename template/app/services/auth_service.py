"""认证服务模块。

提供用户认证和令牌管理功能。
"""

from datetime import datetime, timezone, timedelta
from typing import Any

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.crud.user_repo import refresh_token_repo, user_repo
from app.exceptions import (
    AuthenticationException,
    BusinessException,
    ResourceNotFoundException,
)
from app.models.user import RefreshToken, User
from app.schemas.token import TokenResponse
from app.schemas.user import UserCreate, UserLogin


# Token 黑名单键前缀
ACCESS_TOKEN_BLACKLIST_PREFIX = "access_token_blacklist:"


class AuthService:
    """认证服务类。"""

    @staticmethod
    async def register(
        db: AsyncSession,
        *,
        user_in: UserCreate,
    ) -> User:
        """注册新用户。

        Args:
            db: 数据库会话。
            user_in: 用户创建数据。

        Returns:
            创建的用户实例。

        Raises:
            BusinessException: 如果邮箱或用户名已存在。
        """
        # 检查邮箱是否已存在
        existing_user = await user_repo.get_by_email(db, email=user_in.email)
        if existing_user:
            raise BusinessException(message="邮箱已被注册")

        # 检查用户名是否已存在
        existing_user = await user_repo.get_by_username(db, username=user_in.username)
        if existing_user:
            raise BusinessException(message="用户名已被占用")

        # 创建用户
        user = await user_repo.create(db, obj_in=user_in)
        return user

    @staticmethod
    async def login(
        db: AsyncSession,
        *,
        user_in: UserLogin,
    ) -> TokenResponse:
        """用户登录。

        Args:
            db: 数据库会话。
            user_in: 登录数据。

        Returns:
            令牌响应。

        Raises:
            AuthenticationException: 如果用户名或密码错误。
        """
        # 获取用户（支持邮箱或用户名登录）
        user = await user_repo.get_by_email_or_username(
            db, email_or_username=user_in.username
        )
        if not user:
            raise AuthenticationException(message="用户名或密码错误")

        # 验证密码
        if not verify_password(user_in.password, user.hashed_password):
            raise AuthenticationException(message="用户名或密码错误")

        # 检查账户是否被禁用
        if not user.is_active:
            raise AuthenticationException(message="账户已被禁用")

        # 创建访问令牌
        access_token = create_access_token(subject=str(user.id))

        # 创建刷新令牌
        refresh_token = create_refresh_token(subject=str(user.id))

        # 存储刷新令牌到数据库
        from app.core.config import settings

        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        await refresh_token_repo.create(
            db,
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    @staticmethod
    async def refresh_tokens(
        db: AsyncSession,
        *,
        refresh_token: str,
    ) -> TokenResponse:
        """刷新令牌。

        Args:
            db: 数据库会话。
            refresh_token: 刷新令牌。

        Returns:
            新的令牌响应。

        Raises:
            AuthenticationException: 如果刷新令牌无效。
        """
        # 验证刷新令牌
        token_data = decode_token(refresh_token)
        if not token_data or token_data.get("type") != "refresh":
            raise AuthenticationException(message="无效的刷新令牌")

        # 从数据库获取刷新令牌
        token_obj = await refresh_token_repo.get_valid_by_token(db, token=refresh_token)
        if not token_obj:
            raise AuthenticationException(message="刷新令牌已过期或被撤回")

        # 获取用户信息
        user = await user_repo.get(db, id=token_obj.user_id)
        if not user or not user.is_active:
            raise AuthenticationException(message="用户不存在或已被禁用")

        # 撤回旧的刷新令牌
        token_obj.revoke()
        await db.flush()

        # 创建新的访问令牌
        access_token = create_access_token(subject=str(user.id))

        # 创建新的刷新令牌
        new_refresh_token = create_refresh_token(subject=str(user.id))

        # 存储新的刷新令牌
        from app.core.config import settings

        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        await refresh_token_repo.create(
            db,
            user_id=user.id,
            token=new_refresh_token,
            expires_at=expires_at,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

    @staticmethod
    async def logout(
        db: AsyncSession,
        redis: Redis,
        *,
        access_token: str,
        refresh_token: str,
    ) -> None:
        """用户登出。

        Args:
            db: 数据库会话。
            redis: Redis 客户端。
            access_token: 访问令牌。
            refresh_token: 刷新令牌。
        """
        # 解码 access token 获取过期时间
        token_data = decode_token(access_token)
        if token_data:
            # 计算 token 剩余有效时间
            exp = token_data.get("exp", 0)
            now = int(datetime.now(timezone.utc).timestamp())
            ttl = max(0, exp - now)

            # 如果 token 还有有效期，添加到黑名单
            if ttl > 0:
                blacklist_key = f"{ACCESS_TOKEN_BLACKLIST_PREFIX}{access_token}"
                await redis.setex(blacklist_key, ttl, "1")

        # 撤回刷新令牌
        await refresh_token_repo.revoke(db, token=refresh_token)

    @staticmethod
    async def get_current_user(
        db: AsyncSession,
        redis: Redis,
        *,
        token: str,
    ) -> User:
        """获取当前用户。

        Args:
            db: 数据库会话。
            redis: Redis 客户端。
            token: 访问令牌。

        Returns:
            当前用户实例。

        Raises:
            AuthenticationException: 如果令牌无效或在黑名单中。
            ResourceNotFoundException: 如果用户不存在。
        """
        # 检查 token 是否在黑名单中
        blacklist_key = f"{ACCESS_TOKEN_BLACKLIST_PREFIX}{token}"
        if await redis.exists(blacklist_key):
            raise AuthenticationException(message="令牌已失效")

        # 解码令牌
        token_data = decode_token(token)
        if not token_data or token_data.get("type") != "access":
            raise AuthenticationException(message="无效的访问令牌")

        # 获取用户 ID
        user_id = token_data.get("sub")
        if not user_id:
            raise AuthenticationException(message="无效的令牌载荷")

        # 获取用户
        user = await user_repo.get(db, id=user_id)
        if not user:
            raise ResourceNotFoundException(message="用户不存在")

        if not user.is_active:
            raise AuthenticationException(message="账户已被禁用")

        return user
