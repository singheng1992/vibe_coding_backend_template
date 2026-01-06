"""Pytest 配置文件。

定义测试夹具和测试配置。"""
import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.main import app

# 测试数据库 URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"


# 创建测试数据库引擎
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

# 创建测试会话工厂
test_async_session_maker = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """创建事件循环。

    Yields:
        事件循环。
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话。

    Yields:
        数据库会话。
    """
    # 创建表
    from app.models.base import Base

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 创建会话
    async with test_async_session_maker() as session:
        yield session

    # 清理表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """创建测试客户端。

    Args:
        db_session: 数据库会话。

    Yields:
        异步测试客户端。
    """

    # 覆盖数据库依赖
    async def override_get_db():
        yield db_session

    from app.api.deps import get_db
    from app.main import app

    app.dependency_overrides[get_db] = override_get_db

    # 创建客户端
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # 清理依赖覆盖
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> dict[str, str]:
    """创建测试用户。

    Args:
        db_session: 数据库会话。

    Returns:
        测试用户数据。
    """
    from app.crud.user_repo import user_repo
    from app.schemas.user import UserCreate

    user_in = UserCreate(
        email="test@example.com",
        username="testuser",
        password="Test1234!",
        full_name="测试用户",
    )

    user = await user_repo.create(db_session, obj_in=user_in)
    await db_session.commit()
    await db_session.refresh(user)

    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "password": "Test1234!",
    }


@pytest_asyncio.fixture(scope="function")
async def auth_headers(client: AsyncClient, test_user: dict[str, str]) -> dict[str, str]:
    """获取认证头。

    Args:
        client: 测试客户端。
        test_user: 测试用户。

    Returns:
        认证头字典。
    """
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user["username"],
            "password": test_user["password"],
        },
    )

    data = response.json()
    token = data["data"]["access_token"]

    return {"Authorization": f"Bearer {token}"}
