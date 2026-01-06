"""应用程序入口模块。

创建和配置 FastAPI 应用实例。
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.api.v1.router import api_router
from app.core.cache import close_redis
from app.core.config import settings
from app.core.database import close_db
from app.core.logging import logger
from app.middleware.error_handler import (
    app_exception_handler,
    general_exception_handler,
    validation_exception_handler,
)
from app.middleware.logging import LoggingMiddleware
from app.exceptions import AppException


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用程序生命周期管理。

    Args:
        app: FastAPI 应用实例。

    Yields:
        None
    """
    # 启动时执行
    logger.info("应用程序启动中...")

    # 注意：数据库迁移请使用 Alembic
    # alembic upgrade head

    logger.info("应用程序启动完成")

    yield

    # 关闭时执行
    logger.info("应用程序关闭中...")

    # 关闭 Redis 连接
    await close_redis()
    logger.info("Redis 连接已关闭")

    # 关闭数据库连接
    await close_db()
    logger.info("数据库连接已关闭")

    logger.info("应用程序已关闭")


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="高性能 FastAPI 后端服务",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# 添加 CORS 中间件
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加日志中间件
app.add_middleware(LoggingMiddleware)

# 注册异常处理器
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 注册 API 路由
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# 根路径
@app.get("/", tags=["根路径"])
async def root() -> dict[str, str]:
    """根路径端点。

    Returns:
        欢迎消息。
    """
    return {"message": f"欢迎使用 {settings.APP_NAME} API", "version": settings.APP_VERSION}


# 健康检查
@app.get("/health", tags=["健康检查"])
async def health_check() -> dict[str, Any]:
    """健康检查端点。

    Returns:
        健康状态信息。
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }
