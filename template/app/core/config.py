"""应用程序配置模块。

使用 Pydantic Settings 管理应用程序配置，支持从环境变量和 .env 文件加载。
"""

import secrets
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用程序配置类。

    支持从环境变量和 .env 文件加载配置。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 应用程序基础配置
    APP_NAME: str = Field(default="My API", description="应用程序名称")
    APP_VERSION: str = Field(default="0.1.0", description="应用程序版本")
    DEBUG: bool = Field(default=False, description="调试模式")
    ENVIRONMENT: Literal["development", "testing", "production"] = Field(
        default="development", description="运行环境"
    )

    # API 配置
    API_V1_PREFIX: str = Field(default="/api/v1", description="API v1 路径前缀")

    # 服务器配置
    HOST: str = Field(default="0.0.0.0", description="服务器主机")
    PORT: int = Field(default=8000, description="服务器端口")

    # 安全配置
    SECRET_KEY: str = Field(
        default=secrets.token_urlsafe(32),
        description="JWT 密钥（生产环境必须从环境变量设置）",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="访问令牌过期时间（分钟）"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, description="刷新令牌过期时间（天）"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT 算法")

    # 密码配置
    PASSWORD_BCRYPT_ROUNDS: int = Field(
        default=12, description="密码 bcrypt 加密轮数"
    )

    # 数据库配置
    POSTGRES_HOST: str = Field(default="localhost", description="PostgreSQL 主机")
    POSTGRES_PORT: int = Field(default=5432, description="PostgreSQL 端口")
    POSTGRES_USER: str = Field(default="postgres", description="PostgreSQL 用户")
    POSTGRES_PASSWORD: str = Field(default="postgres", description="PostgreSQL 密码")
    POSTGRES_DB: str = Field(default="mydb", description="PostgreSQL 数据库名")

    @property
    def DATABASE_URL(self) -> str:
        """获取数据库连接 URL."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Redis 配置
    REDIS_HOST: str = Field(default="localhost", description="Redis 主机")
    REDIS_PORT: int = Field(default=6379, description="Redis 端口")
    REDIS_PASSWORD: str | None = Field(default=None, description="Redis 密码")
    REDIS_DB: int = Field(default=0, description="Redis 数据库编号")

    # RabbitMQ 配置
    RABBITMQ_HOST: str = Field(default="localhost", description="RabbitMQ 主机")
    RABBITMQ_PORT: int = Field(default=5672, description="RabbitMQ 端口")
    RABBITMQ_USER: str = Field(default="guest", description="RabbitMQ 用户")
    RABBITMQ_PASSWORD: str = Field(default="guest", description="RabbitMQ 密码")
    RABBITMQ_VHOST: str = Field(default="/", description="RabbitMQ 虚拟主机")

    # MinIO 配置
    MINIO_ENDPOINT: str = Field(default="localhost:9000", description="MinIO 端点")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", description="MinIO 访问密钥")
    MINIO_SECRET_KEY: str = Field(default="minioadmin", description="MinIO 密钥")
    MINIO_SECURE: bool = Field(default=False, description="MinIO 是否使用 HTTPS")
    MINIO_BUCKET: str = Field(default="my-bucket", description="MinIO 存储桶名称")

    # CORS 配置
    CORS_ORIGINS: list = Field(
        default=["http://localhost:3000,http://localhost:8000"],
        description="允许的 CORS 源（逗号分隔）"
    )

    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")

    # 分页配置
    DEFAULT_PAGE_SIZE: int = Field(default=20, description="默认分页大小")
    MAX_PAGE_SIZE: int = Field(default=100, description="最大分页大小")


# 全局配置实例
settings = Settings()
