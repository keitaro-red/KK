FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.26 /uv /uvx /bin/

WORKDIR /app

ENV TZ=Asia/Shanghai

RUN sed -i 's|deb.debian.org|mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y libpq5 \
    && apt-get clean

COPY backend/pyproject.toml /app/pyproject.toml
COPY backend/.python-version /app/.python-version
COPY backend/package /app/package
# ENV UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/


RUN uv sync --no-dev

COPY backend/server /app/server


CMD ["uv", "run", "--no-sync", "uvicorn", "server.main:app", "--reload", "--host", "0.0.0.0", "--port", "5050"]