"""AgentRun 数据访问"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kk.models.agent_run import AgentRun


class AgentRunRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_run(self, run_id, thread_id, uid, agent_slug, query) -> AgentRun:
        run = AgentRun(
            id=run_id,
            thread_id=thread_id,
            uid=uid,
            agent_slug=agent_slug,
            query=query,
            status="pending",
        )
        self.db.add(run)
        await self.db.flush()
        return run

    async def get_run(self, run_id) -> AgentRun | None:
        """从数据库获取run_id的AgentRun"""
        result = await self.db.execute(select(AgentRun).where(AgentRun.id == run_id))
        return result.scalar_one_or_none()

    async def mark_running(self, run_id) -> None:
        """改AgentRun的状态为running"""
        run = await self.get_run(run_id)
        if run:
            run.status = "running"

    async def mark_terminal(self, run_id, status, error_message=None) -> None:
        """改变run状态"""
        run = await self.get_run(run_id)
        if run:
            run.status = status
            run.error_message = error_message
