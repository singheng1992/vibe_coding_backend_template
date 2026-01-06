"""日志中间件。

记录请求和响应信息，支持请求 ID 链路追踪。
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件。

    记录每个请求的处理时间和响应状态。
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """处理请求。

        Args:
            request: HTTP 请求对象。
            call_next: 下一个中间件或路由处理器。

        Returns:
            HTTP 响应对象。
        """
        # 获取请求 ID
        request_id = getattr(request.state, "request_id", "unknown")

        # 记录请求开始
        start_time = time.time()

        # 记录请求信息
        logger.info(
            f"请求开始: {request.method} {request.url.path}",
            extra={"request_id": request_id},
        )

        # 处理请求
        try:
            response = await call_next(request)

            # 计算处理时间
            process_time = time.time() - start_time

            # 添加自定义响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)

            # 记录响应信息
            logger.info(
                f"请求完成: {request.method} {request.url.path} - "
                f"状态码: {response.status_code} - "
                f"处理时间: {process_time:.3f}s",
                extra={"request_id": request_id},
            )

            return response

        except Exception as e:
            # 计算处理时间
            process_time = time.time() - start_time

            # 记录错误
            logger.error(
                f"请求失败: {request.method} {request.url.path} - "
                f"错误: {str(e)} - "
                f"处理时间: {process_time:.3f}s",
                extra={"request_id": request_id},
                exc_info=True,
            )

            raise
