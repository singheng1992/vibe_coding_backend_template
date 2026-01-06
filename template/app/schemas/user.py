"""用户 Schema 模块。

定义用户相关的请求和响应 Schema。
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用户基础 Schema。"""

    email: EmailStr = Field(..., description="用户邮箱")
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    full_name: str | None = Field(None, max_length=100, description="用户显示名称")


class UserCreate(UserBase):
    """用户创建 Schema。"""

    password: str = Field(..., min_length=8, max_length=100, description="密码")


class UserUpdate(BaseModel):
    """用户更新 Schema。"""

    email: EmailStr | None = Field(None, description="用户邮箱")
    full_name: str | None = Field(None, max_length=100, description="用户显示名称")
    password: str | None = Field(None, min_length=8, max_length=100, description="密码")


class UserLogin(BaseModel):
    """用户登录 Schema。"""

    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户响应 Schema。"""

    id: uuid.UUID = Field(..., description="用户 ID")
    email: str = Field(..., description="用户邮箱")
    username: str = Field(..., description="用户名")
    full_name: str | None = Field(None, description="用户显示名称")
    is_active: bool = Field(..., description="账户是否启用")
    is_superuser: bool = Field(..., description="是否为超级管理员")
    is_verified: bool = Field(..., description="邮箱是否已验证")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        """Pydantic 配置。"""

        from_attributes = True
