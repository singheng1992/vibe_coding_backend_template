"""用户端点。

提供用户管理相关的接口。
"""

from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.api.deps import CurrentSuperuserDep, CurrentUserDep, DatabaseDep
from app.schemas.base import ApiResponse, PageResponse
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get(
    "/me",
    response_model=ApiResponse[UserResponse],
    summary="获取当前用户信息",
    description="获取当前登录用户的详细信息",
)
async def get_user_me(
    db: DatabaseDep,
    current_user: CurrentUserDep,
) -> ApiResponse[UserResponse]:
    """获取当前用户信息。

    Args:
        db: 数据库会话。
        current_user: 当前用户实例。

    Returns:
        包含用户信息的响应。
    """
    user = await UserService.get_user_me(db=db, current_user=current_user)
    return ApiResponse.success(data=UserResponse.model_validate(user))


@router.patch(
    "/me",
    response_model=ApiResponse[UserResponse],
    summary="更新当前用户信息",
    description="更新当前登录用户的信息",
)
async def update_user_me(
    db: DatabaseDep,
    current_user: CurrentUserDep,
    user_in: UserUpdate,
) -> ApiResponse[UserResponse]:
    """更新当前用户信息。

    Args:
        db: 数据库会话。
        current_user: 当前用户实例。
        user_in: 更新数据。

    Returns:
        包含更新后用户信息的响应。
    """
    user = await UserService.update_user_me(
        db=db, current_user=current_user, user_in=user_in
    )
    return ApiResponse.success(data=UserResponse.model_validate(user))


@router.get(
    "/{user_id}",
    response_model=ApiResponse[UserResponse],
    summary="获取用户信息",
    description="根据 ID 获取指定用户的详细信息",
)
async def get_user(
    db: DatabaseDep,
    user_id: str,
    current_super_user: CurrentSuperuserDep,
) -> ApiResponse[UserResponse]:
    """获取用户信息。

    Args:
        db: 数据库会话。
        user_id: 用户 ID。
        current_super_user: 当前超级管理员用户。

    Returns:
        包含用户信息的响应。
    """
    user = await UserService.get_user(db, user_id=user_id)
    return ApiResponse.success(data=UserResponse.model_validate(user))


@router.patch(
    "/{user_id}",
    response_model=ApiResponse[UserResponse],
    summary="更新用户信息",
    description="更新指定用户的信息",
)
async def update_user(
    db: DatabaseDep,
    user_id: str,
    user_in: UserUpdate,
    current_super_user: CurrentSuperuserDep,
) -> ApiResponse[UserResponse]:
    """更新用户信息。

    Args:
        db: 数据库会话。
        user_id: 用户 ID。
        user_in: 更新数据。
        current_super_user: 当前超级管理员用户。

    Returns:
        包含更新后用户信息的响应。
    """
    user = await UserService.update_user(db, user_id=user_id, user_in=user_in)
    return ApiResponse.success(data=UserResponse.model_validate(user))


@router.delete(
    "/{user_id}",
    summary="删除用户",
    description="软删除指定用户",
)
async def delete_user(
    db: DatabaseDep,
    user_id: str,
    current_super_user: CurrentSuperuserDep,
) -> Response:
    """删除用户。

    Args:
        db: 数据库会话。
        user_id: 用户 ID。
        current_super_user: 当前超级管理员用户。

    Returns:
        空响应，状态码 204。
    """
    await UserService.delete_user(db, user_id=user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "",
    response_model=ApiResponse[PageResponse],
    summary="获取用户列表",
    description="分页获取用户列表",
)
async def get_users(
    db: DatabaseDep,
    current_super_user: CurrentSuperuserDep,
    skip: Annotated[int, Query(ge=0, description="跳过的记录数")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="返回的记录数")] = 20,
) -> ApiResponse[PageResponse]:
    """获取用户列表。

    Args:
        db: 数据库会话。
        current_super_user: 当前超级管理员用户。
        skip: 跳过的记录数。
        limit: 返回的记录数。

    Returns:
        包含用户列表的响应。
    """
    from app.core.config import settings

    limit = min(limit, settings.MAX_PAGE_SIZE)
    page_data = await UserService.get_users(db, skip=skip, limit=limit)
    return ApiResponse.success(data=page_data)
