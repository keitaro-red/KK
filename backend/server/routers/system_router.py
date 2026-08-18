"""系统路由"""
from fastapi import APIRouter
from sqlalchemy import text

system = APIRouter(prefix="/system", tags=["system"])


@system.get("/health")
async def health_check():
    """系统健康检查 数据库连通"""
    from kk.storage.postgres.manager import pg_manager

    db_ok = False
    if pg_manager.is_initialized:
        try:
            async with pg_manager.get_session() as session:
                await session.execute(text("SELECT 1"))
                db_ok = True
        except Exception:
            pass
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
    }
