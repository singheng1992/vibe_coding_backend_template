"""验证器模块。

提供数据验证相关的工具函数。
"""

import re
from typing import Any


def validate_username(username: str) -> bool:
    """验证用户名格式。

    用户名必须:
    - 长度在 3-50 个字符之间
    - 只包含字母、数字、下划线和连字符
    - 以字母开头

    Args:
        username: 用户名。

    Returns:
        是否有效。
    """
    if not username or len(username) < 3 or len(username) > 50:
        return False
    pattern = r"^[a-zA-Z][a-zA-Z0-9_-]*$"
    return bool(re.match(pattern, username))


def validate_password_strength(password: str) -> tuple[bool, str]:
    """验证密码强度。

    密码必须:
    - 长度至少 8 个字符
    - 包含至少一个大写字母
    - 包含至少一个小写字母
    - 包含至少一个数字
    - 包含至少一个特殊字符

    Args:
        password: 密码。

    Returns:
        (是否有效, 错误消息) 元组。
    """
    if not password or len(password) < 8:
        return False, "密码长度至少为 8 个字符"

    if not re.search(r"[A-Z]", password):
        return False, "密码必须包含至少一个大写字母"

    if not re.search(r"[a-z]", password):
        return False, "密码必须包含至少一个小写字母"

    if not re.search(r"\d", password):
        return False, "密码必须包含至少一个数字"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "密码必须包含至少一个特殊字符"

    return True, ""


def sanitize_string(value: Any, max_length: int = 255) -> str | None:
    """清理字符串。

    去除首尾空格，限制最大长度。

    Args:
        value: 输入值。
        max_length: 最大长度。

    Returns:
        清理后的字符串，如果输入不是字符串则返回 None。
    """
    if not isinstance(value, str):
        return None
    return value.strip()[:max_length]
