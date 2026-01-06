"""日期时间工具模块。

提供日期时间相关的工具函数。
"""

from datetime import datetime, timezone


def now_utc() -> datetime:
    """获取当前 UTC 时间。

    Returns:
        当前 UTC 时间。
    """
    return datetime.now(timezone.utc)


def datetime_to_iso(dt: datetime) -> str:
    """将 datetime 转换为 ISO 格式字符串。

    Args:
        dt: datetime 对象。

    Returns:
        ISO 格式字符串。
    """
    return dt.isoformat()


def iso_to_datetime(iso_str: str) -> datetime:
    """将 ISO 格式字符串转换为 datetime。

    Args:
        iso_str: ISO 格式字符串。

    Returns:
        datetime 对象。
    """
    return datetime.fromisoformat(iso_str)
