"""创建管理员用户脚本。

创建一个超级管理员账户。
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_redis
from app.core.database import async_session_maker
from app.core.security import get_password_hash
from app.core.logging import logger
from app.crud.user_repo import user_repo
from app.models.user import User
from app.schemas.user import UserCreate


async def create_admin_user(
    email: str,
    username: str,
    password: str,
    full_name: str = "系统管理员",
) -> User:
    """创建管理员用户。

    Args:
        email: 管理员邮箱。
        username: 管理员用户名。
        password: 管理员密码。
        full_name: 管理员显示名称。

    Returns:
        创建的管理员用户实例。
    """
    user_in = UserCreate(
        email=email,
        username=username,
        password=password,
        full_name=full_name,
    )

    async with async_session_maker() as db:
        # 检查用户是否已存在
        existing_user = await user_repo.get_by_email(db, email=email)
        if existing_user:
            logger.warning(f"管理员用户已存在: {email}")
            return existing_user

        existing_user = await user_repo.get_by_username(db, username=username)
        if existing_user:
            logger.warning(f"管理员用户名已存在: {username}")
            return existing_user

        # 创建用户
        user = await user_repo.create(db, obj_in=user_in)

        # 设置为超级管理员和已验证
        user.is_superuser = True
        user.is_verified = True
        user.is_active = True

        await db.commit()
        await db.refresh(user)

        logger.info(f"管理员用户创建成功: {user.email} (username: {user.username})")
        return user


async def main() -> None:
    """主函数。"""
    import getpass

    logger.info("开始创建管理员用户...")

    # 获取管理员信息
    email = input("请输入管理员邮箱 [默认: admin@example.com]: ").strip()
    if not email:
        email = "admin@example.com"

    username = input("请输入管理员用户名 [默认: admin]: ").strip()
    if not username:
        username = "admin"

    full_name = input("请输入管理员显示名称 [默认: 系统管理员]: ").strip()
    if not full_name:
        full_name = "系统管理员"

    # 获取密码
    while True:
        password = getpass.getpass("请输入管理员密码 (至少8位): ")
        if len(password) < 8:
            print("密码长度至少为 8 位，请重新输入。")
            continue

        confirm_password = getpass.getpass("请确认密码: ")
        if password != confirm_password:
            print("两次输入的密码不一致，请重新输入。")
            continue

        break

    # 创建管理员用户
    try:
        admin = await create_admin_user(
            email=email,
            username=username,
            password=password,
            full_name=full_name,
        )
        print(f"\n✓ 管理员用户创建成功!")
        print(f"  邮箱: {admin.email}")
        print(f"  用户名: {admin.username}")
        print(f"  显示名称: {admin.full_name}")
        print(f"  ID: {admin.id}")
    except Exception as e:
        logger.error(f"创建管理员用户失败: {e}")
        print(f"\n✗ 创建管理员用户失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
