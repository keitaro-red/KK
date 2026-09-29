"""Run 生命周期服务 
存Message，存Run，消息入队
"""
import json
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from kk.repositories.conversation_repository import ConversationRepository
from kk.repositories.agent_run_repository import AgentRunRepository
from kk.services.run_worker import enqueue_run

async def create_agent_run_view(*,query:str,agent_slug,thread_id:str,current_uid:str,db:AsyncSession):
    """
    创建 run 线程
    存message 创Run 入队
    """
    repo = ConversationRepository(db)

    # 解析线程 没传则新建，传了则校验是否是当前用户的
    if thread_id:
        conversation = await repo.get_conversation_by_thread_id(thread_id)
        if conversation is None or conversation.uid != current_uid:
            raise ValueError("对话线程不存在")
    else:
        conversation = await repo.create_conversation(uid=current_uid)
        thread_id = conversation.thread_id 

    # 存 Message 存进数据库
    message = await repo.add_message(thread_id,role="user",content=query)
    if message is None:
        raise ValueError("保存信息失败")

    # 创建 Run 存进数据库
    run_id = str(uuid.uuid4())
    run_repo = AgentRunRepository(db)
    await run_repo.create_run(
        run_id=run_id,
        thread_id=thread_id,
        uid=current_uid,
        agent_slug=agent_slug,
        input_message_id=message.id,
    )
    await db.commit()

    # 入队
    await enqueue_run(run_id)

    return {"run_id":run_id,"thread_id":thread_id,"status":"pending"}

async def create_resume_run(*,run_id:str,decision:dict,current_uid:str,db:AsyncSession):
    """
    从断点恢复run：
    校验run_id是否存在，新建一个run_type为resume的run，resume_decision为decision（形如{"decisions":[{"type":"approve"}]}）
    """
    run_repo = AgentRunRepository(db)

    # 原run存在且属于当前用户
    origin = await run_repo.get_run_for_user(run_id,current_uid)
    if origin is None:
        raise ValueError("运行任务不存在")

    # 校验状态是否为interrupted
    if origin.status != "interrupted":
        raise ValueError(f"当前状态不可恢复：{origin.status}")

    # 新建run，继承原run的thread_id和agent_slug
    new_run_id = str(uuid.uuid4())
    await run_repo.create_run(
        run_id=new_run_id,
        thread_id=origin.thread_id,
        uid=current_uid,
        agent_slug=origin.agent_slug,
        input_message_id=None,
        run_type="resume",
        resume_decision=json.dumps(decision,ensure_ascii=False),
    )
    await db.commit()

    # 入队
    await enqueue_run(new_run_id)

    return {"run_id":new_run_id,"thread_id":origin.thread_id,"status":"pending"}


