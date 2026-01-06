"""用户数据访问层测试。"""
import pytest


@pytest.mark.asyncio
class TestUserRepo:
    """用户数据访问层测试类。"""

    async def test_create_user(self, db_session: AsyncSession) -> None:
        """测试创建用户。"""
        from app.crud.user_repo import user_repo
        from app.schemas.user import UserCreate

        user_in = UserCreate(
            email="repo@example.com",
            username="repouser",
            password="Password123!",
        )

        user = await user_repo.create(db_session, obj_in=user_in)
        await db_session.commit()

        assert user.email == "repo@example.com"
        assert user.username == "repouser"
        assert user.hashed_password is not None

    async def test_get_by_email(self, db_session: AsyncSession, test_user: dict) -> None:
        """测试通过邮箱获取用户。"""
        from app.crud.user_repo import user_repo

        user = await user_repo.get_by_email(db_session, email=test_user["email"])

        assert user is not None
        assert user.email == test_user["email"]

    async def test_get_by_username(self, db_session: AsyncSession, test_user: dict) -> None:
        """测试通过用户名获取用户。"""
        from app.crud.user_repo import user_repo

        user = await user_repo.get_by_username(db_session, username=test_user["username"])

        assert user is not None
        assert user.username == test_user["username"]
