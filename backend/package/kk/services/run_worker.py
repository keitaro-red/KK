"""ARQ worker:离线执行Agent run"""
from langchain_core.messages import HumanMessage
from arq.connections import RedisSettings

from kk.config import config
from kk.repositories.agent_run_repository import AgentRunRepository
from kk.storage.postgres.manager import pg_manager
from kk.storage.redis.manager import close_redis
from kk.agents.buildin import agent_manager
from kk.services.run_queue_service import append_run_event

async def process_agent_run(ctx,run_id:str):
    """根据run_id执行队列中的 AgentRun ：
    加载任务-> 流式 -> 写事件流 -> 终态"""
    # 加载任务
    async with pg_manager.get_session() as db:
        repo = AgentRunRepository(db)
        run =await repo.get_run(run_id)
        if run is None:
            return

        # 标记运行
        await repo.mark_running(run_id)

    # 流式执行 Agent
    try:
        agent = agent_manager.get_agent("ChatbotAgent")
        messages = [HumanMessage(content=run.query)]
        async for msg,metadata in agent.stream_messages_with_state(
            messages,
            input_context={"uid":run.uid,"thread_id":run.thread_id},
        ):
            content = getattr(msg,"content","")
            if content:
                await append_run_event(run_id,"message",{"content":content})

        # 终态完成
        await append_run_event(run_id,"end",{"status":"completed"})
        async with pg_manager.get_session() as db:
            repo = AgentRunRepository(db)
            await repo.mark_terminal(run_id,"completed")

    except Exception as e:
        # 终态失败
        await append_run_event(run_id,"end",{"status":"failed","error":str(e)})
        async with pg_manager.get_session() as db:
            repo = AgentRunRepository(db)
            await repo.mark_terminal(run_id,"failed",error_message=str(e))


async def _worker_startup(ctx):
    pg_manager.initialize()
    await pg_manager.create_tables()

async def _worker_shutdown(ctx):
    await pg_manager.close()
    await close_redis()

class WorkerSettings:
    """ARQ Worker 配置"""

    functions = [process_agent_run]
    on_startup = _worker_startup
    on_shutdown = _worker_shutdown
    redis_settings=RedisSettings.from_dsn(config.REDIS_URL)