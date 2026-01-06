"""令牌 Schema 模块。

定义 JWT 令牌相关的 Schema。
"""

from pydantic import BaseModel, Field


class TokenPayload(BaseModel):
    """令牌载荷 Schema。

    Attributes:
        sub: 令牌主题（通常是用户 ID）。
        exp: 过期时间。
        type: 令牌类型（access 或 refresh）。
    """

    sub: str = Field(..., description="令牌主题")
    exp: int = Field(..., description="过期时间戳")
    type: str = Field(..., description="令牌类型")


class TokenResponse(BaseModel):
    """令牌响应 Schema。

    Attributes:
        access_token: 访问令牌。
        refresh_token: 刷新令牌。
        token_type: 令牌类型。
    """

    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
