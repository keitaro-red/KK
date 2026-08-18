"""生命周期管理"""
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    """KK 应用生命周期管理"""
    # ------启动阶段
    print("KK backend starting...")
    from kk.storage.postgres.manager import pg_manager

    # 初始化数据库连接
    pg_manager.initialize()
    await pg_manager.create_tables()
    print("PostgreSQL connected,tables created")

    print("KK backend started")
    yield
    # 关闭阶段
    print("KK backend shutting down...")

    await pg_manager.close()
    print("PostgreSQL connection closed")

    print("KK backend stopped")
