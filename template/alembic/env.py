"""Alembic 环境配置。

配置数据库迁移环境。
"""
import sys
from pathlib import Path

# 添加项目根目录到 sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from logging.config import fileConfig
from typing import AsyncGenerator

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# 导入配置和模型
from app.core.config import settings
from app.models.base import Base

# 导入所有模型以确保它们被注册到 Base.metadata
from app.models.user import User, RefreshToken  # noqa: F401

# Alembic 配置对象
config = context.config

# 设置数据库 URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# 解释配置文件中的 Python 日志配置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 设置 MetaData 对象
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """在'离线'模式下运行迁移。

    这不会连接数据库，而是生成 SQL 脚本。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """执行迁移。

    Args:
        connection: 数据库连接。
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """在异步模式下运行迁移。"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """在'在线'模式下运行迁移。

    这种模式下会连接数据库并执行迁移。
    """
    import asyncio

    asyncio.run(run_async_migrations())


# 根据上下文判断运行模式
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
