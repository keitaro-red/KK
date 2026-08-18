"""PostgreSQL管理器"""
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from kk.config import config


class PostgresManager:
    """PostgreSQL 管理器"""

    def __init__(self):
        self._engine = None
        self._session_factory = None
        self._initialized = False

    def initialize(self):
        """初始化数据库连接 创建连接池+会话工厂"""
        if self._initialized:
            return

        db_url = config.POSTGRES_URL
        if not db_url:
            raise RuntimeError("POSTGRES_URL 未设置，请在.env中配置")

        # Engine = 连接池管理
        self._engine = create_async_engine(
            db_url,
            pool_pre_ping=True,     # 连接前ping
            pool_recycle=1800,      # 30分钟回收连接
            pool_size=5,            # 保持5个连接
            max_overflow=10,        # 最多额外开10个
        )

        # Session 工厂 每次调用创建新的对话
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        self._initialized = True

    async def create_tables(self):
        """创建所有表结构 根据Model定义自动执行CREATE TABLE"""
        from kk.models.user import Base

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def get_session(self):
        """获取一个数据库会话（自动 commit / rollback / close）"""
        if not self._initialized:
            raise RuntimeError("PostgresManager 未初始化")

        session = self._session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def close(self):
        """关闭连接"""
        if self._engine:
            await self._engine.dispose()

    @property
    def is_initialized(self) -> bool:
        return self._initialized


pg_manager = PostgresManager()
