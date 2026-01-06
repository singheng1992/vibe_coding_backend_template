"""认证端点。

提供用户注册、登录、登出和令牌刷新等接口。
"""

from fastapi import APIRouter, Header, status

from app.api.deps import CurrentUserDep, DatabaseDep, RedisDep
from app.schemas.base import ApiResponse
from app.schemas.token import TokenResponse
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="创建新用户账户",
)
async def register(
    db: DatabaseDep,
    user_in: UserCreate,
) -> ApiResponse[UserResponse]:
    """用户注册。

    Args:
        db: 数据库会话。
        user_in: 用户创建数据。

    Returns:
        包含用户信息的响应。
    """
    user = await AuthService.register(db, user_in=user_in)
    return ApiResponse.success(data=UserResponse.model_validate(user))


@router.post(
    "/login",
    response_model=ApiResponse[TokenResponse],
    summary="用户登录",
    description="使用用户名/邮箱和密码登录",
)
async def login(
    db: DatabaseDep,
    user_in: UserLogin,
) -> ApiResponse[TokenResponse]:
    """用户登录。

    Args:
        db: 数据库会话。
        user_in: 登录数据。

    Returns:
        包含访问令牌和刷新令牌的响应。
    """
    tokens = await AuthService.login(db, user_in=user_in)
    return ApiResponse.success(data=tokens)


@router.post(
    "/refresh",
    response_model=ApiResponse[TokenResponse],
    summary="刷新令牌",
    description="使用刷新令牌获取新的访问令牌",
)
async def refresh_tokens(
    db: DatabaseDep,
    refresh_token: str,
) -> ApiResponse[TokenResponse]:
    """刷新令牌。

    Args:
        db: 数据库会话。
        refresh_token: 刷新令牌。

    Returns:
        包含新令牌的响应。
    """
    from fastapi import Body

    tokens = await AuthService.refresh_tokens(db, refresh_token=refresh_token)
    return ApiResponse.success(data=tokens)


@router.post(
    "/logout",
    response_model=ApiResponse[None],
    summary="用户登出",
    description="撤回访问令牌和刷新令牌，用户登出",
)
async def logout(
    db: DatabaseDep,
    redis: RedisDep,
    refresh_token: str,
    authorization: str = Header(..., description="Bearer token"),
) -> ApiResponse[None]:
    """用户登出。

    Args:
        db: 数据库会话。
        redis: Redis 客户端。
        refresh_token: 刷新令牌。
        authorization: Authorization 头，包含 access token。

    Returns:
        成功响应。
    """
    # 从 Authorization 头中提取 access token
    access_token = authorization.replace("Bearer ", "")
    await AuthService.logout(db, redis=redis, access_token=access_token, refresh_token=refresh_token)
    return ApiResponse.success(message="登出成功")


@router.get(
    "/me",
    response_model=ApiResponse[UserResponse],
    summary="获取当前用户",
    description="获取当前登录用户的信息",
)
async def get_current_user_info(
    current_user: CurrentUserDep,
) -> ApiResponse[UserResponse]:
    """获取当前用户信息。

    Args:
        current_user: 当前用户实例。

    Returns:
        包含用户信息的响应。
    """
    return ApiResponse.success(data=UserResponse.model_validate(current_user))
