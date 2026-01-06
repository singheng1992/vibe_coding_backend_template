# FastAPI 后端项目模板

基于 Python 3.11、FastAPI、PostgreSQL 的高性能后端项目模板。

## 技术栈

- **Web 框架**: FastAPI 0.128.0
- **ASGI 服务器**: Uvicorn 0.40.0
- **数据库**: PostgreSQL 15.0+ (AsyncPG 0.31.0)
- **ORM**: SQLAlchemy 2.0.45 (异步模式)
- **数据库迁移**: Alembic 1.13.0
- **缓存**: Redis 7.0+ (Redis 7.1.0)
- **消息队列**: RabbitMQ (aio-pika 9.4.0)
- **对象存储**: MinIO (minio 7.2.20)
- **认证**: JWT (pyjwt 2.8.0)
- **密码加密**: Bcrypt (bcrypt 4.0.1)
- **数据验证**: Pydantic 2.12.5
- **日志**: Loguru 0.7.3
- **测试**: pytest 8.3.4

## 项目结构

```
my-project/
├── app/
│   ├── main.py                 # 应用入口
│   ├── api/                    # API 层
│   │   ├── deps.py             # API 依赖
│   │   └── v1/                 # API v1
│   │       ├── router.py       # 路由聚合
│   │       └── endpoints/      # 端点
│   ├── core/                   # 核心配置
│   │   ├── config.py           # 配置管理
│   │   ├── security.py         # 安全相关
│   │   ├── database.py         # 数据库连接
│   │   ├── logging.py          # 日志配置
│   │   └── dependencies.py     # 全局依赖
│   ├── models/                 # 数据库模型
│   ├── schemas/                # Pydantic Schema
│   ├── crud/                   # 数据访问层
│   ├── services/               # 业务逻辑层
│   ├── utils/                  # 工具函数
│   ├── middleware/             # 中间件
│   └── exceptions.py           # 自定义异常
├── tests/                      # 测试
├── alembic/                    # 数据库迁移
├── scripts/                    # 脚本
├── .env.example                # 环境变量示例
├── pyproject.toml              # 项目配置
├── alembic.ini                 # Alembic 配置
├── docker-compose.yml          # Docker Compose
└── Dockerfile                  # Docker 镜像
```

## 快速开始

### 环境要求

- Python 3.11+
- PostgreSQL 15.0+
- Redis 7.0+
- RabbitMQ
- MinIO (可选)

### 本地开发

1. **克隆项目**

```bash
git clone <repository_url>
cd my-project
```

2. **安装依赖**

```bash
# 安装 uv (推荐)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装项目依赖
uv sync --dev
```

3. **配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息
```

4. **启动基础设施服务**

```bash
# 使用 Docker Compose 启动
docker-compose up -d postgres redis rabbitmq minio
```

5. **初始化数据库**

```bash
# 运行数据库迁移
alembic upgrade head

# 创建管理员用户
python scripts/create_admin.py

# 填充测试数据（可选）
python scripts/seed_data.py
```

6. **启动应用**

```bash
# 开发模式（自动重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用 uv
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. **访问 API 文档**

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Docker 部署

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f app
```

## API 规范

### 统一响应格式

成功响应：
```json
{
    "code": 200,
    "message": "success",
    "data": {...}
}
```

错误响应：
```json
{
    "code": 400,
    "message": "错误描述",
    "detail": "详细错误信息"
}
```

分页响应：
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "items": [...],
        "meta": {
            "total": 100,
            "page": 1,
            "size": 20,
            "pages": 5,
            "has_next": true,
            "has_prev": false
        }
    }
}
```

### 认证接口

- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新令牌
- `POST /api/v1/auth/logout` - 用户登出
- `GET /api/v1/auth/me` - 获取当前用户

### 用户接口

- `GET /api/v1/users` - 获取用户列表
- `GET /api/v1/users/{id}` - 获取用户详情
- `GET /api/v1/users/me` - 获取当前用户信息
- `PATCH /api/v1/users/me` - 更新当前用户信息
- `PATCH /api/v1/users/{id}` - 更新用户信息
- `DELETE /api/v1/users/{id}` - 删除用户

## 开发规范

### 命名规范

- 文件名: `snake_case`
- 类名: `PascalCase`
- 函数/变量: `snake_case`
- 常量: `UPPER_SNAKE_CASE`

### 代码风格

```bash
# 代码格式化
ruff format .

# 代码检查
ruff check .

# 类型检查
mypy app/
```

### 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_api/test_auth.py

# 查看覆盖率
pytest --cov=app --cov-report=html
```

### 数据库迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 查看迁移历史
alembic history
```

## 配置说明

主要配置项在 `.env` 文件中：

- `SECRET_KEY`: JWT 密钥（生产环境必须修改）
- `DATABASE_URL`: 数据库连接 URL
- `REDIS_HOST`: Redis 主机地址
- `RABBITMQ_HOST`: RabbitMQ 主机地址
- `CORS_ORIGINS`: 允许的跨域源

## 许可证

MIT License
