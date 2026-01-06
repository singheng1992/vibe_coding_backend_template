"""错误处理中间件。

统一处理应用程序中的异常，返回标准化的错误响应。
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.logging import logger
from app.exceptions import (
    AppException,
    AuthenticationException,
    BusinessException,
    ConflictException,
    PermissionException,
    RateLimitException,
    ResourceNotFoundException,
    ValidationException,
)


async def app_exception_handler(
    request: Request,
    exc: AppException,
) -> JSONResponse:
    """处理应用程序自定义异常。

    Args:
        request: HTTP 请求对象。
        exc: 应用程序异常。

    Returns:
        JSON 错误响应。
    """
    request_id = getattr(request.state, "request_id", "unknown")

    logger.bind(request_id=request_id, exception_type=type(exc).__name__, code=exc.code).error(
        f"业务异常: {exc.message}"
    )

    return JSONResponse(
        status_code=exc.code,
        content={
            "code": exc.code,
            "message": exc.message,
            "detail": exc.detail,
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: ValidationError,
) -> JSONResponse:
    """处理 Pydantic 验证异常。

    Args:
        request: HTTP 请求对象。
        exc: 验证异常。

    Returns:
        JSON 错误响应。
    """
    request_id = getattr(request.state, "request_id", "unknown")

    logger.bind(request_id=request_id, exception_type="ValidationError").warning(
        "验证异常"
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "数据验证失败",
            "detail": exc.errors(),
        },
    )


async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """处理通用异常。

    Args:
        request: HTTP 请求对象。
        exc: 异常。

    Returns:
        JSON 错误响应。
    """
    request_id = getattr(request.state, "request_id", "unknown")

    logger.bind(request_id=request_id, exception_type=type(exc).__name__).error(
        f"未处理的异常: {str(exc)}",
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "服务器内部错误",
            "detail": str(exc) if exc else None,
        },
    )
