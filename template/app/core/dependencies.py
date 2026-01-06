"""全局依赖模块。

提供 API 端点使用的全局依赖注入。
"""

from collections.abc import AsyncGenerator

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import logger


async def get_request_id(x_request_id: str | None = Header(None)) -> str:
    """获取或生成请求 ID。

    Args:
        x_request_id: 请求头中的请求 ID。

    Returns:
        请求 ID 字符串。
    """
    if x_request_id:
        return x_request_id
    import uuid

    return str(uuid.uuid4())


class RequestIdMiddleware:
    """请求 ID 中间件。"""

    def __init__(self, app) -> None:
        """初始化中间件。

        Args:
            app: ASGI 应用实例。
        """
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        """处理请求。

        Args:
            scope: ASGI scope。
            receive: ASGI receive callable。
            send: ASGI send callable。
        """
        if scope["type"] == "http":
            # 从请求头中获取 request_id
            headers = dict(scope.get("headers", []))
            request_id = headers.get(b"x-request-id")
            if request_id:
                request_id = request_id.decode()
            else:
                import uuid

                request_id = str(uuid.uuid4())

            # 将 request_id 添加到 scope
            scope["request_id"] = request_id

            # 配置 loguru 的 context
            with logger.contextualize(request_id=request_id):
                await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)


__all__ = ["get_request_id", "RequestIdMiddleware", "get_db"]
