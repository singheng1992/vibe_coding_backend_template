"""日志配置模块。

配置结构化日志，支持请求 ID 链路追踪。
"""

import sys
from pathlib import Path

from loguru import logger as _logger

from app.core.config import settings


def setup_logging() -> None:
    """配置应用程序日志。

    移除默认的处理器，添加自定义的格式化和过滤器。
    """
    # 移除默认处理器
    _logger.remove()

    # 定义日志格式（使用默认值避免 KeyError）
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{extra[request_id]}</cyan> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # 添加默认 request_id 的日志格式化器
    def formatter(record):
        """格式化日志记录，确保 request_id 有默认值。"""
        if "request_id" not in record["extra"]:
            record["extra"]["request_id"] = "N/A"
        return log_format

    # 添加控制台处理器
    _logger.add(
        sys.stdout,
        format=formatter,
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # 添加文件处理器（按日期轮转）
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)

    _logger.add(
        log_path / "app_{time:YYYY-MM-DD}.log",
        format=formatter,
        level=settings.LOG_LEVEL,
        rotation="00:00",  # 每天午夜轮转
        retention="30 days",  # 保留 30 天
        compression="zip",  # 压缩旧日志
        backtrace=True,
        diagnose=True,
    )

    # 添加错误日志文件
    _logger.add(
        log_path / "error_{time:YYYY-MM-DD}.log",
        format=formatter,
        level="ERROR",
        rotation="00:00",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
    )


# 初始化日志配置
setup_logging()

# 导出 logger，绑定默认的 request_id
logger = _logger.bind(request_id="N/A")
