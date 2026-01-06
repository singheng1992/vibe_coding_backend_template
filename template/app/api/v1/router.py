"""API v1 路由聚合。"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users

api_router = APIRouter()

# 认证路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 用户路由
api_router.include_router(users.router, prefix="/users", tags=["用户"])
