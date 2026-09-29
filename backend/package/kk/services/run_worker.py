"""ARQ worker:离线执行Agent run"""
import json
import asyncio
from dataclasses import dataclass, field
from arq import create_pool
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from arq.connections import RedisSettings
from sqlalchemy import select
from pathlib import Path

from kk.config import config
from kk.models.agent_run import TERMINAL_RUN_STATUSES
from kk.models.conversation import Message
from kk.repositories.agent_run_repository import AgentRunRepository
from kk.storage.postgres.manager import pg_manager
from kk.storage.redis.manager import close_redis
from kk.agents.buildin import agent_manager
from kk.services.run_queue_service import append_run_event, has_cancel_signal, clear_cancel_signal
from kk.repositories.conversation_repository import ConversationRepository



# ============================================================
# 生产者侧：把 run 投进队列（这段在 API 进程里被调用）
# ============================================================

# ARQ 连接池，模块级单例。注意是"每个进程一份"——API 进程调 enqueue_run 时
# 创建的是 API 侧的池；worker 进程有自己的池，两者不共享。

# API侧的 ARQ 连接池（全局单例）
_pool = None


async def get_arq_pool():
    """获取全局 ARQ 连接池，第一次调用时创建，之后复用（惰性创建）"""
    global _pool
    if _pool is None:
        _pool = await create_pool(RedisSettings.from_dsn(config.REDIS_URL))
    return _pool


async def enqueue_run(run_id: str):
    """把 run_id 对应的 run 放到 worker 队列，被服务层调用 """
    pool = await get_arq_pool()
    await pool.enqueue_job("process_agent_run", run_id)


# ============================================================
# 取消监听：RunContext（下面 process_agent_run 在 worker 进程里用它）
# ============================================================

@dataclass
class RunContext:
    """run 执行时的取消监听的上下文"""

    run_id: str
    cancel_event: asyncio.Event = field(
        default_factory=asyncio.Event)      # 取消标识
    _watch_task: asyncio.Task | None = None

    async def start(self):
        """开始一个后台任务，开始监听取消信号"""
        self._watch_task = asyncio.create_task(self._watch_cancel_signal())

    async def close(self):
        """清理，取消后台任务（跑完，失败，取消）"""
        if self._watch_task:
            self._watch_task.cancel()
            await asyncio.gather(self._watch_task, return_exceptions=True)

    async def wait_cancelled(self):
        """挂起，直到cancel_event被set"""
        await self.cancel_event.wait()

    async def _watch_cancel_signal(self):
        """后台循环：每0.2秒查一次Redis，查到取消就set cancel_event并结束"""
        while not self.cancel_event.is_set():
            if await has_cancel_signal(self.run_id):
                self.cancel_event.set()
                return
            await asyncio.sleep(0.2)


async def _comsume_stream_with_cancel(agen, run_ctx: RunContext):
    """竞速函数，token与取消信号竞速"""
    while True:
        next_task = asyncio.create_task(
            agen.__anext__())           # A:取下一个token
        cancel_task = asyncio.create_task(run_ctx.wait_cancelled())  # B:等取消
        # 谁先到算谁
        done, _ = await asyncio.wait({next_task, cancel_task}, return_when=asyncio.FIRST_COMPLETED)

        if cancel_task in done:     # 取消先到，取消token，通知上层写cancelled终态
            next_task.cancel()
            await asyncio.gather(next_task, return_exceptions=True)
            raise asyncio.CancelledError(f"{run_ctx.run_id} cancelled")

        cancel_task.cancel()        # token先到，先不取消
        await asyncio.gather(cancel_task, return_exceptions=True)
        try:
            yield next_task.result()  # 交出token
        except StopAsyncIteration:
            return


# ============================================================
# 消费者侧：worker 真正执行 run（ARQ 从队列取到 run_id 后调它）
# ============================================================
async def _persist_asistant_message(thread_id: str, content: str)->None:
    """
    把 assistant 消息落库
    (新开session)
    """
    if not content.strip():
        return
    async with pg_manager.get_session() as db:
        await ConversationRepository(db).add_message(
            thread_id,role="assistant",content=content,
        )

async def process_agent_run(ctx, run_id: str):
    """
    加载run_id执行队列中的 AgentRun任务，输出消息：
    加载任务-> 监听 -> 终态"""
    # 加载任务、输入正文
    async with pg_manager.get_session() as db:
        repo = AgentRunRepository(db)
        run = await repo.get_run(run_id)
        if run is None or run.status in TERMINAL_RUN_STATUSES:
            return

        query = None
        if run.run_type == "resume":    # resume 没有输入正文
            pass
        else:
            # 从Message表加载输入正文
            result = await db.execute(select(Message).where(Message.id == run.input_message_id))
            input_message = result.scalar_one_or_none()
            if input_message is None:
                # 输入消息被删 终态设为 failed
                await repo.mark_terminal(run_id, "failed", error_message="输入消息不存在")
                await db.commit()
                return
            query = input_message.content

        # 状态改为运行
        await repo.mark_running(run_id)
        await db.commit()

    # 监听
    run_ctx = RunContext(run_id=run_id)
    await run_ctx.start()

    # 模型回复缓冲区(用于最后落库)
    buffer:list[str]=[]

    # 流式执行 Agent
    try:
        agent = agent_manager.get_agent("ChatbotAgent")

        if run.run_type == "resume":
            decision = json.loads(run.resume_decision or "{}")
            graph_input = Command(resume=decision)
        else:
            graph_input = None
        
        messages = [HumanMessage(content=query or "")] if graph_input is None else None
        # 流式生成器交给竞速
        stream = agent.stream_messages_with_state(
            messages,
            input_context={"uid": run.uid, "thread_id": run.thread_id},
            graph_input=graph_input,
        )

        # 竞速消费：正常逐个 yeild token；取消时抛异常
        async for msg, metadata in _comsume_stream_with_cancel(stream, run_ctx):
            # print("[probe]",type(msg).__name__,
            #       "| type=",getattr(msg,"type",None),
            #       "| content_type=",type(getattr(msg, "content", None)).__name__,
            #       "| chunks=",getattr(msg, "tool_call_chunks", None),
            #       "| tc=" ,getattr(msg, "tool_call", None),
            #       "| chunks_pos=",getattr(msg, "chunk_position", None),flush=True)
            content = getattr(msg, "content", "")
            if content:
                buffer.append(content)  # 累积模型回复
                await append_run_event(run_id, "message", {"content": content})

        # ==============
        # 流式执行结束 判断是真完成还是挂在中断上
        interrupts = await agent.get_pending_interrupt(input_context={"uid": run.uid, "thread_id": run.thread_id})
        if interrupts:
            # 挂在中断上，终态为 interrupted
            # 落库模型回复
            await _persist_asistant_message(run.thread_id, "".join(buffer))
            await append_run_event(run_id, "interrupt",{"interrupts":[getattr(i,"value",i) for i in interrupts]})
            await append_run_event(run_id, "end", {"status": "interrupted"})
            async with pg_manager.get_session() as db:
                await AgentRunRepository(db).mark_terminal(run_id, "interrupted")
                await db.commit()
            return

        # 正常完成，终态为 completed
        # 落库模型回复
        await _persist_asistant_message(run.thread_id, "".join(buffer))
        await append_run_event(run_id, "end", {"status": "completed"})
        async with pg_manager.get_session() as db:
            await AgentRunRepository(db).mark_terminal(run_id, "completed")
            await db.commit()

    except asyncio.CancelledError as e:
        # 被取消，终态为 cancelled 
        # 落库模型回复
        await _persist_asistant_message(run.thread_id, "".join(buffer))
        await append_run_event(run_id, "end", {"status": "cancelled"})
        async with pg_manager.get_session() as db:
            await AgentRunRepository(db).mark_terminal(run_id, "cancelled")
            await db.commit()

    except Exception as e:
        # 终态失败，终态为 failed 加错误信息
        # 落库模型回复
        await _persist_asistant_message(run.thread_id, "".join(buffer))
        await append_run_event(run_id, "end", {"status": "failed", "error": str(e)})
        async with pg_manager.get_session() as db:
            repo = AgentRunRepository(db)
            await repo.mark_terminal(run_id, "failed", error_message=str(e))

    finally:
        # 无论完成与否，清理取消监听信号
        await run_ctx.close()
        await clear_cancel_signal(run_id)


async def _worker_startup(ctx):
    pg_manager.initialize()
    await pg_manager.create_tables()
    Path(config.WORKSPACE_DIR).mkdir(parents=True, exist_ok=True) # 确保工作目录存在，否则会报错。


async def _worker_shutdown(ctx):
    await pg_manager.close()
    await close_redis()


class WorkerSettings:
    """ARQ Worker 配置"""

    functions = [process_agent_run]
    on_startup = _worker_startup
    on_shutdown = _worker_shutdown
    redis_settings = RedisSettings.from_dsn(config.REDIS_URL)
