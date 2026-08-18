import os
import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.routers import router
from server.utils.lifespan import lifespan

# ------ CORS 配置 ------

DEFAULT_CORS_ORIGINS = ("http://localhost:5173", "http://127.0.0.1:5173")


def _parse_cors_origins() -> list[str]:
    """解析 CORS 允许的来源"""
    value = os.getenv("KK_CORS_ORIGINS")
    if value:
        return [origin.strip() for origin in value.split(",") if origin.strip()]

    environment = (os.getenv("KK_ENV") or "development").strip().lower()
    if environment in {"production", "prod"}:
        return []

    return list(DEFAULT_CORS_ORIGINS)

# ------ APP ------


app = FastAPI(
    title="KK",
    version="0.1.0",
    lifespan=lifespan,
)

# 挂载业务路由
app.include_router(router, prefix="/api")

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors_origins(),
    allow_credentials=True,
    allow_methods=["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"],
    allow_headers=["Accept", "Authorization",
                   "Content-Type", "Last-Event-ID", "X-Requested-With"],
    expose_headers=["Content-Disposition"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server.main:app",
        host="0.0.0.0",
        port=5050,
        reload=True,
        reload_dirs=["server", "package"],
    )
