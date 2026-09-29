"""AgentRun 数据访问"""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kk.models.agent_run import AgentRun, TERMINAL_RUN_STATUSES


class AgentRunRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_run(self, run_id, thread_id, uid, agent_slug, 
                         input_message_id=None,run_type="chat",resume_decision=None) -> AgentRun:
        """创建run进程信息，保存到数据库"""
        run = AgentRun(
            id=run_id,
            thread_id=thread_id,
            uid=uid,
            agent_slug=agent_slug,
            input_message_id=input_message_id,      # 替换query
            run_type=run_type,
            resume_decision=resume_decision,
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
        if run and run.status not in TERMINAL_RUN_STATUSES:
            run.status = "running"
            run.started_at = datetime.utcnow()

    async def get_run_for_user(self, run_id, uid) -> AgentRun | None:
        """根据uid和run_id返回run线程，同时匹配才能获取"""
        result = await self.db.execute(
            select(AgentRun).where(AgentRun.id == run_id, AgentRun.uid == uid)
        )
        return result.scalar_one_or_none()

    async def request_cancel(self, run_id) -> None:
        """改变run状态为取消状态"""
        run = await self.get_run(run_id)
        if run and run.status not in TERMINAL_RUN_STATUSES:
            run.status = "cancel_requested"

    async def mark_terminal(self, run_id, status, error_message=None) -> None:
        """改变run状态为终态，结束此run"""
        run = await self.get_run(run_id)
        if run and run.status not in TERMINAL_RUN_STATUSES:
            run.status = status
            run.error_message = error_message
            run.finished_at = datetime.utcnow()
