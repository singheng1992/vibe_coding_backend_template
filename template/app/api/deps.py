"""API 依赖模块。

提供 API 端点使用的依赖注入函数。
"""

from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_redis
from app.core.database import get_db
from app.core.dependencies import get_request_id
from app.models.user import User
from app.services.auth_service import AuthService

# HTTP Bearer 认证
security = HTTPBearer()

# 数据库会话依赖
DatabaseDep = Annotated[AsyncSession, Depends(get_db)]

# Redis 客户端依赖
RedisDep = Annotated[Redis, Depends(get_redis)]

# 请求 ID 依赖
RequestIDDep = Annotated[str, Depends(get_request_id)]

# 认证凭据依赖
CredentialsDep = Annotated[HTTPAuthorizationCredentials, Depends(security)]


async def get_current_user(
    db: DatabaseDep,
    redis: RedisDep,
    credentials: CredentialsDep,
) -> User:
    """获取当前用户。

    Args:
        db: 数据库会话。
        redis: Redis 客户端。
        credentials: HTTP Bearer 认证凭据。

    Returns:
        当前用户实例。

    Raises:
        AuthenticationException: 如果令牌无效或在黑名单中。
        ResourceNotFoundException: 如果用户不存在。
    """
    return await AuthService.get_current_user(db, redis=redis, token=credentials.credentials)


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """获取当前活跃用户。

    Args:
        current_user: 当前用户实例。

    Returns:
        当前活跃用户实例。

    Raises:
        AuthenticationException: 如果用户已被禁用。
    """
    if not current_user.is_active:
        from app.exceptions import AuthenticationException

        raise AuthenticationException(message="账户已被禁用")
    return current_user


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """获取当前超级管理员用户。

    Args:
        current_user: 当前用户实例。

    Returns:
        当前超级管理员用户实例。

    Raises:
        PermissionException: 如果用户不是超级管理员。
    """
    if not current_user.is_superuser:
        from app.exceptions import PermissionException

        raise PermissionException(message="权限不足")
    return current_user


# 类型别名
CurrentUserDep = Annotated[User, Depends(get_current_user)]
CurrentActiveUserDep = Annotated[User, Depends(get_current_active_user)]
CurrentSuperuserDep = Annotated[User, Depends(get_current_superuser)]
