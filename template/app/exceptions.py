"""自定义异常模块。

定义应用程序中使用的自定义异常类。
"""

from typing import Any


class AppException(Exception):
    """应用程序基础异常类。

    所有自定义异常的基类，支持错误码和详细信息。
    """

    def __init__(
        self,
        message: str,
        code: int = 500,
        detail: str | None = None,
    ) -> None:
        """初始化异常。

        Args:
            message: 错误消息。
            code: HTTP 状态码。
            detail: 详细错误信息。
        """
        self.message = message
        self.code = code
        self.detail = detail
        super().__init__(message)


class BusinessException(AppException):
    """业务异常。

    用于处理业务逻辑中的错误情况，如业务规则违反等。

    Attributes:
        message: 错误消息。
        code: HTTP 状态码，默认 400。
        detail: 详细错误信息。
    """

    def __init__(
        self,
        message: str,
        code: int = 400,
        detail: str | None = None,
    ) -> None:
        """初始化业务异常。

        Args:
            message: 错误消息。
            code: HTTP 状态码，默认 400。
            detail: 详细错误信息。
        """
        super().__init__(message=message, code=code, detail=detail)


class AuthenticationException(AppException):
    """认证异常。

    用于处理身份验证失败的情况。

    Attributes:
        message: 错误消息。
        code: HTTP 状态码，默认 401。
        detail: 详细错误信息。
    """

    def __init__(
        self,
        message: str = "认证失败",
        code: int = 401,
        detail: str | None = None,
    ) -> None:
        """初始化认证异常。

        Args:
            message: 错误消息。
            code: HTTP 状态码，默认 401。
            detail: 详细错误信息。
        """
        super().__init__(message=message, code=code, detail=detail)


class PermissionException(AppException):
    """权限异常。

    用于处理权限不足的情况。

    Attributes:
        message: 错误消息。
        code: HTTP 状态码，默认 403。
        detail: 详细错误信息。
    """

    def __init__(
        self,
        message: str = "权限不足",
        code: int = 403,
        detail: str | None = None,
    ) -> None:
        """初始化权限异常。

        Args:
            message: 错误消息。
            code: HTTP 状态码，默认 403。
            detail: 详细错误信息。
        """
        super().__init__(message=message, code=code, detail=detail)


class ResourceNotFoundException(AppException):
    """资源未找到异常。

    用于处理请求的资源不存在的情况。

    Attributes:
        message: 错误消息。
        code: HTTP 状态码，默认 404。
        detail: 详细错误信息。
    """

    def __init__(
        self,
        message: str = "资源未找到",
        code: int = 404,
        detail: str | None = None,
    ) -> None:
        """初始化资源未找到异常。

        Args:
            message: 错误消息。
            code: HTTP 状态码，默认 404。
            detail: 详细错误信息。
        """
        super().__init__(message=message, code=code, detail=detail)


class ValidationException(AppException):
    """验证异常。

    用于处理数据验证失败的情况。

    Attributes:
        message: 错误消息。
        code: HTTP 状态码，默认 422。
        detail: 详细错误信息。
    """

    def __init__(
        self,
        message: str = "数据验证失败",
        code: int = 422,
        detail: str | None = None,
    ) -> None:
        """初始化验证异常。

        Args:
            message: 错误消息。
            code: HTTP 状态码，默认 422。
            detail: 详细错误信息。
        """
        super().__init__(message=message, code=code, detail=detail)


class ConflictException(AppException):
    """冲突异常。

    用于处理资源冲突的情况，如重复创建等。

    Attributes:
        message: 错误消息。
        code: HTTP 状态码，默认 409。
        detail: 详细错误信息。
    """

    def __init__(
        self,
        message: str = "资源冲突",
        code: int = 409,
        detail: str | None = None,
    ) -> None:
        """初始化冲突异常。

        Args:
            message: 错误消息。
            code: HTTP 状态码，默认 409。
            detail: 详细错误信息。
        """
        super().__init__(message=message, code=code, detail=detail)


class RateLimitException(AppException):
    """限流异常。

    用于处理请求超过频率限制的情况。

    Attributes:
        message: 错误消息。
        code: HTTP 状态码，默认 429。
        detail: 详细错误信息。
    """

    def __init__(
        self,
        message: str = "请求过于频繁",
        code: int = 429,
        detail: str | None = None,
    ) -> None:
        """初始化限流异常。

        Args:
            message: 错误消息。
            code: HTTP 状态码，默认 429。
            detail: 详细错误信息。
        """
        super().__init__(message=message, code=code, detail=detail)


__all__ = [
    "AppException",
    "BusinessException",
    "AuthenticationException",
    "PermissionException",
    "ResourceNotFoundException",
    "ValidationException",
    "ConflictException",
    "RateLimitException",
]
