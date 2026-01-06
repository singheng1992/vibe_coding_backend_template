"""安全相关模块。

包含 JWT 令牌处理和密码加密功能。
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from app.core.config import settings

# 类型别名，保持向后兼容
JWTError = InvalidTokenError

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码。

    Args:
        plain_password: 明文密码。
        hashed_password: 哈希后的密码。

    Returns:
        密码是否匹配。
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希值。

    Args:
        password: 明文密码。

    Returns:
        哈希后的密码。
    """
    return pwd_context.hash(password)


def create_access_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
) -> str:
    """创建访问令牌。

    Args:
        subject: 令牌主题（通常是用户 ID）。
        expires_delta: 过期时间增量。

    Returns:
        JWT 访问令牌。
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"sub": str(subject), "exp": expire, "type": "access"}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
) -> str:
    """创建刷新令牌。

    Args:
        subject: 令牌主题（通常是用户 ID）。
        expires_delta: 过期时间增量。

    Returns:
        JWT 刷新令牌。
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode = {"sub": str(subject), "exp": expire, "type": "refresh"}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any] | None:
    """解码令牌。

    Args:
        token: JWT 令牌。

    Returns:
        解码后的令牌数据，如果令牌无效则返回 None。
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
