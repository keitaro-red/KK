"""模型对话路由"""
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from kk.config import config
from kk.models.chat import select_model
from kk.models.user import User
from kk.utils.sse_utils import format_sse
from server.utils.auth_middleware import get_required_user,get_db
from kk.repositories.conversation_repository import ConversationRepository


chat = APIRouter(prefix="/chat", tags=["chat"])


class ChatCallRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000, description="用户输入")
    thread_id: str | None = None  # 可选：新对话无


class ChatCallResponse(BaseModel):
    response: str

@chat.get("/threads")
async def list_threads(
    user:User=Depends(get_required_user),
    db:AsyncSession=Depends(get_db),
):
    """获取当前用户的对话列表"""
    repo = ConversationRepository(db)
    conversations=  await repo.list_conversations(user.uid)
    return [
        {
            "thread_id":c.thread_id,
            "title":c.title,
            "created_at":c.created_at.isoformat(),
            "updated_at":c.updated_at.isoformat(),
        }
        for c in conversations
    ]

@chat.post("/thread")
async def create_thread(
    user:User=Depends(get_required_user),
    db:AsyncSession=Depends(get_db),
):
    """创建新对话"""
    repo=ConversationRepository(db)
    conversation=await repo.create_conversation(uid=user.uid)
    return {
        "thread_id":conversation.thread_id,
        "title":conversation.title
    }

@chat.get("/thread/{thread_id}/messages")
async def get_messages(
    thread_id:str,
    user:User=Depends(get_required_user),
    db: AsyncSession=Depends(get_db),
):
    """获取对话的历史消息"""
    repo = ConversationRepository(db)
    conversation = await repo.get_conversation_by_thread_id(thread_id)
    if not conversation or conversation.uid !=user.uid:
        raise HTTPException(status_code=404,detail="对话不存在")

    messages=await repo.get_message_by_thread_id(thread_id)
    return [
        {"role":m.role,"content":m.content}
        for m in messages
    ]


@chat.post("/call", response_model=ChatCallResponse)
async def call_llm(
    data: ChatCallRequest,
    user: User = Depends(get_required_user),
):
    """非流式调用LLM，一次性返回完整回复"""
    adapter = select_model(config.DEFAULT_MODEL)
    reply = await adapter.call(data.query)
    return ChatCallResponse(response=reply)


@chat.post("/stream", tags=["stream"])
async def stream_llm(
    data: ChatCallRequest,
    user: User = Depends(get_required_user),
    db:AsyncSession=Depends(get_db),
):
    """流式调用LLM，逐个token返回，并且持久化消息"""
    repo = ConversationRepository(db)

    # 解析thread_id
    thread_id=data.thread_id
    if not thread_id:
        conversation = await repo.create_conversation(uid=user.uid)
        thread_id=conversation.thread_id

    # 开始前保存消息
    await repo.add_message(thread_id,role="user",content=data.query)

    # 流式生成
    async def event_generator():
        adapter = select_model(config.DEFAULT_MODEL)
        chunks=[]
        async for token in adapter.stream(data.query):
            chunks.append(token)
            yield format_sse({"content": token}, "message")

        # 结束，保存assistant 消息+传回thread_id
        await repo.add_message(thread_id,role="assistant",content="".join(chunks))
        yield format_sse({"content": "", "thread_id":thread_id},"done")

    

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
