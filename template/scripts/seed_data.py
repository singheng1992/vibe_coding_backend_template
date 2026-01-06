"""测试数据填充脚本。

填充测试数据到数据库。"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.core.security import get_password_hash
from app.core.logging import logger
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService


async def create_test_user(db: AsyncSession) -> None:
    """创建测试用户。

    Args:
        db: 数据库会话。
    """
    # 检查是否已存在测试用户
    from app.crud.user_repo import user_repo

    existing_user = await user_repo.get_by_email(db, email="test@example.com")
    if existing_user:
        logger.info("测试用户已存在，跳过创建")
        return

    # 创建测试用户
    user_in = UserCreate(
        email="test@example.com",
        username="testuser",
        password="Test1234!",
        full_name="测试用户",
    )

    user = await AuthService.register(db, user_in=user_in)
    logger.info(f"创建测试用户成功: {user.email}")


async def main() -> None:
    """主函数。"""
    logger.info("开始填充测试数据...")

    async with async_session_maker() as db:
        await create_test_user(db)
        await db.commit()

    logger.info("测试数据填充完成")


if __name__ == "__main__":
    asyncio.run(main())
