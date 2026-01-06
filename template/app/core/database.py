"""数据库连接模块。

管理数据库连接池和会话。
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

# 创建异步数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# 创建异步会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话。

    Yields:
        数据库会话。

    Examples:
        ```python
        @app.get("/users/{user_id}")
        async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
            user = await user_service.get(db, user_id)
            return user
        ```
    """
    async with async_session_maker() as session:
        try:
            yield session
            # 成功后提交事务
            await session.commit()
        except Exception:
            # 失败时回滚事务
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db() -> None:
    """关闭数据库连接。"""
    await engine.dispose()
