"""认证 API 测试。"""
import pytest


@pytest.mark.asyncio
class TestAuthAPI:
    """认证 API 测试类。"""

    async def test_register_success(self, client: AsyncClient) -> None:
        """测试成功注册。"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "Password123!",
                "full_name": "新用户",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "success"
        assert data["data"]["email"] == "newuser@example.com"
        assert data["data"]["username"] == "newuser"

    async def test_register_duplicate_email(self, client: AsyncClient, test_user: dict) -> None:
        """测试重复邮箱注册。"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user["email"],
                "username": "another",
                "password": "Password123!",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert data["code"] == 400
        assert "邮箱" in data["message"]

    async def test_login_success(self, client: AsyncClient, test_user: dict) -> None:
        """测试成功登录。"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user["username"],
                "password": test_user["password"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]

    async def test_login_wrong_password(self, client: AsyncClient, test_user: dict) -> None:
        """测试错误密码登录。"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user["username"],
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert data["code"] == 401

    async def test_get_current_user(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """测试获取当前用户信息。"""
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "email" in data["data"]


# 导入 AsyncClient 类型
from httpx import AsyncClient
