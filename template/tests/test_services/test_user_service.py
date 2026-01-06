"""用户服务测试。"""
import pytest


@pytest.mark.asyncio
class TestUserService:
    """用户服务测试类。"""

    async def test_get_user(self, db_session: AsyncSession, test_user: dict) -> None:
        """测试获取用户。"""
        from app.services.user_service import UserService

        user = await UserService.get_user(db_session, user_id=test_user["id"])

        assert user.email == test_user["email"]
        assert user.username == test_user["username"]

    async def test_get_user_not_found(self, db_session: AsyncSession) -> None:
        """测试获取不存在的用户。"""
        from app.services.user_service import UserService
        from app.exceptions import ResourceNotFoundException

        with pytest.raises(ResourceNotFoundException):
            await UserService.get_user(db_session, user_id="00000000-0000-0000-0000-000000000000")

    async def test_get_users(self, db_session: AsyncSession) -> None:
        """测试获取用户列表。"""
        from app.services.user_service import UserService

        page_data = await UserService.get_users(db_session, skip=0, limit=10)

        assert page_data.items is not None
        assert page_data.meta.total >= 0
