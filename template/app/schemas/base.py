"""基础 Schema 模块。

定义通用的响应 Schema。
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

DataType = TypeVar("DataType")


class MetaResponse(BaseModel):
    """分页元数据响应。

    Attributes:
        total: 总记录数。
        page: 当前页码。
        size: 每页数量。
        pages: 总页数。
        has_next: 是否有下一页。
        has_prev: 是否有上一页。
    """

    total: int = Field(..., description="总记录数", ge=0)
    page: int = Field(..., description="当前页码", ge=1)
    size: int = Field(..., description="每页数量", ge=1)
    pages: int = Field(..., description="总页数", ge=0)
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")


class PageResponse(BaseModel, Generic[DataType]):
    """分页响应。

    Attributes:
        items: 数据列表。
        meta: 分页元数据。
    """

    items: list[DataType] = Field(default_factory=list, description="数据列表")
    meta: MetaResponse = Field(..., description="分页元数据")

    @classmethod
    def create(
        cls,
        items: list[DataType],
        total: int,
        page: int,
        size: int,
    ) -> "PageResponse[DataType]":
        """创建分页响应。

        Args:
            items: 数据列表。
            total: 总记录数。
            page: 当前页码。
            size: 每页数量。

        Returns:
            分页响应对象。
        """
        pages = (total + size - 1) // size if size > 0 else 0
        has_next = page < pages
        has_prev = page > 1

        return cls(
            items=items,
            meta=MetaResponse(
                total=total,
                page=page,
                size=size,
                pages=pages,
                has_next=has_next,
                has_prev=has_prev,
            ),
        )


class ApiResponse(BaseModel, Generic[DataType]):
    """统一 API 响应格式。

    Attributes:
        code: 状态码。
        message: 响应消息。
        data: 响应数据。
        detail: 详细错误信息（可选）。
    """

    code: int = Field(..., description="状态码")
    message: str = Field(..., description="响应消息")
    data: DataType | None = Field(default=None, description="响应数据")
    detail: str | None = Field(default=None, description="详细错误信息")

    @classmethod
    def success(
        cls,
        data: DataType | None = None,
        message: str = "success",
    ) -> "ApiResponse[DataType]":
        """创建成功响应。

        Args:
            data: 响应数据。
            message: 响应消息。

        Returns:
            API 响应对象。
        """
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(
        cls,
        code: int,
        message: str,
        detail: str | None = None,
    ) -> "ApiResponse[None]":
        """创建错误响应。

        Args:
            code: 错误码。
            message: 错误消息。
            detail: 详细错误信息。

        Returns:
            API 响应对象。
        """
        return cls(code=code, message=message, detail=detail)
