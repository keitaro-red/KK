"""Postgres checkpoint 单例"""
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from kk.config import config

_saver : AsyncPostgresSaver | None = None
_pool : AsyncConnectionPool | None = None

def _psycopg_dsn()->str:
    """把 KK 的async DSN 转换为 psycopg 数据库连接的 DSN
    KK 的 POSTGRES_URL 格式为：postgresql+asyncpg://...  （SQLAlchemy 格式），
    psycopg 数据库连接的 DSN 格式为：postgresql://...
    """
    return config.POSTGRES_URL.replace("+asyncpg","")

async def get_checkpointer()->AsyncPostgresSaver:
    """获取 Postgres checkpoint （惰性创建+建表）"""
    global _saver, _pool
    if _saver is None:
        _pool = AsyncConnectionPool(
            _psycopg_dsn(),
            open=False,
            kwargs={
                "autocommit": True,         # 自动提交事务
                "prepare_threshold": 0,     # 不预编译语句
                "row_factory": dict_row,      # 返回字典格式的行
            },
        )
        await _pool.open()
        _saver = AsyncPostgresSaver(_pool)
        await _saver.setup()        # 建checkpoint 元数据表
    return _saver
