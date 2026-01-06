"""辅助工具函数模块。

提供通用的辅助函数。
"""

import hashlib
import secrets
import string
from typing import Any


def generate_random_string(length: int = 32) -> str:
    """生成随机字符串。

    Args:
        length: 字符串长度。

    Returns:
        随机字符串。
    """
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_hash(content: str, algorithm: str = "sha256") -> str:
    """生成内容的哈希值。

    Args:
        content: 要哈希的内容。
        algorithm: 哈希算法，默认为 sha256。

    Returns:
        十六进制哈希字符串。
    """
    hash_func = hashlib.new(algorithm)
    hash_func.update(content.encode("utf-8"))
    return hash_func.hexdigest()


def mask_sensitive_data(
    data: str,
    visible_start: int = 4,
    visible_end: int = 4,
    mask_char: str = "*",
) -> str:
    """掩码敏感数据。

    Args:
        data: 敏感数据。
        visible_start: 开头可见字符数。
        visible_end: 结尾可见字符数。
        mask_char: 掩码字符。

    Returns:
        掩码后的字符串。

    Examples:
        >>> mask_sensitive_data("user@example.com")
        'user***@example.com'
        >>> mask_sensitive_data("1234567890", 3, 3)
        '123****890'
    """
    if len(data) <= visible_start + visible_end:
        return mask_char * len(data)

    start = data[:visible_start]
    end = data[-visible_end:] if visible_end > 0 else ""
    mask_length = len(data) - visible_start - visible_end
    mask = mask_char * mask_length

    return f"{start}{mask}{end}"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断文本。

    Args:
        text: 要截断的文本。
        max_length: 最大长度。
        suffix: 截断后添加的后缀。

    Returns:
        截断后的文本。
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def deep_get(
    data: dict[str, Any],
    key_path: str,
    default: Any = None,
) -> Any:
    """从嵌套字典中获取值。

    Args:
        data: 字典数据。
        key_path: 键路径，用点号分隔，如 "user.profile.name"。
        default: 默认值。

    Returns:
        获取的值，如果不存在则返回默认值。

    Examples:
        >>> data = {"user": {"profile": {"name": "Alice"}}}
        >>> deep_get(data, "user.profile.name")
        'Alice'
        >>> deep_get(data, "user.profile.age", 0)
        0
    """
    keys = key_path.split(".")
    value = data

    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default

    return value
