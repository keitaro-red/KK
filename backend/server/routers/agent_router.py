"""Agent 对话路由"""
import uuid
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from arq import create_pool
from arq.connections import RedisSettings

from kk.agents.buildin import agent_manager
from kk.models.user import User
from server.utils.auth_middleware import get_required_user
from kk.utils.sse_utils import format_sse
from kk.config import config
from server.utils.auth_middleware import get_db
from kk.repositories.agent_run_repository import AgentRunRepository
from kk.services.run_queue_service import list_run_events, publish_cancel_signal
from kk.services.agent_run_service import create_agent_run_view

agent = APIRouter(prefix="/agent", tags=["agent"])

_pool = None


async def _get_arq_pool():
    global _pool
    if _pool is None:
        _pool = await create_pool(RedisSettings.from_dsn(config.REDIS_URL))
    return _pool


class AgentRunRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000, description="用户输入")
    thread_id: str | None = Field(default=None, description="对话线程ID，缺少则新建")


@agent.post('/runs')
async def create_run(
    data: AgentRunRequest,
    user: User = Depends(get_required_user),
    db: AsyncSession = Depends(get_db)
):
    """创建 run 并入队，立即返回 run_id"""
    result = await create_agent_run_view(
        query=data.query,
        agent_slug="ChatbotAgent",
        thread_id=data.thread_id,   # 可能为None
        current_uid=user.uid,
        db=db,
    )

    return result


@agent.post("/runs/{run_id}/cancel")
async def cancel_run(run_id: str, user: User = Depends(get_required_user), db=Depends(get_db)):
    """请求取消一个Run线程"""
    repo = AgentRunRepository(db)
    run = await repo.get_run_for_user(run_id, user.uid)
    if run is None:
        raise HTTPException(status_code=404, detail="运行任务不存在")
    await repo.request_cancel(run_id)
    await db.commit()
    await publish_cancel_signal(run_id)
    return {"run_id":run_id,"status":"cancel_requested"}

@agent.get("runs/{run_id}")
async def get_run_status(run_id:str,user:User=Depends(get_required_user),db=Depends(get_db)):
    """查询 run 状态"""
    repo = AgentRunRepository(db)
    run = await repo.get_run_for_user(run_id,user.uid)
    if run is None:
        raise HTTPException(status_code=404, detail="运行任务不存在")
    return {"run_id":run_id,"status":run.status,"error_message":run.error_message}


@agent.get("/runs/{run_id}/events")
async def stream_run_events(run_id: str, user: User = Depends(get_required_user)):
    """SSE端点：轮询Redis Stream 返回 run 事件"""

    async def event_generator():
        after_seq = "0-0"

        while True:
            events = await list_run_events(run_id, after_seq=after_seq, limit=200)
            for event in events:
                after_seq = event["seq"]
                yield format_sse(event["payload"], event=event["event_type"])
                if event["event_type"] == "end":
                    return
            await asyncio.sleep(0.2)
    return StreamingResponse(event_generator(), media_type="text/event-stream")
