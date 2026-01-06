# 多阶段构建 Dockerfile

# 阶段 1: 构建阶段
FROM python:3.11-slim AS builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 复制项目文件
COPY pyproject.toml ./

# 安装依赖
RUN uv sync --frozen --no-dev

# 阶段 2: 运行阶段
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制虚拟环境
COPY --from=builder /app/.venv /app/.venv

# 复制应用程序代码
COPY ./app ./app
COPY ./alembic ./alembic
COPY ./alembic.ini ./alembic.ini

# 创建日志目录
RUN mkdir -p logs

# 设置环境变量
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
