"""用户 API 测试。"""
import pytest


@pytest.mark.asyncio
class TestUsersAPI:
    """用户 API 测试类。"""

    async def test_get_users(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """测试获取用户列表。"""
        response = await client.get(
            "/api/v1/users",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]

    async def test_get_user_me(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """测试获取当前用户信息。"""
        response = await client.get(
            "/api/v1/users/me",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    async def test_update_user_me(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """测试更新当前用户信息。"""
        response = await client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"full_name": "更新的用户名"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["full_name"] == "更新的用户名"

    async def test_unauthorized_access(self, client: AsyncClient) -> None:
        """测试未授权访问。"""
        response = await client.get("/api/v1/users/me")

        assert response.status_code == 401


# 导入 AsyncClient 类型
from httpx import AsyncClient
