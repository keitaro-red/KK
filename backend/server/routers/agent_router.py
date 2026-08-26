"""Agent 对话路由"""
import uuid

from fastapi import APIRouter,Depends
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from pydantic import BaseModel,Field

from kk.agents.buildin import agent_manager
from kk.models.user import User
from server.utils.auth_middleware import get_required_user
from kk.utils.sse_utils import format_sse


agent = APIRouter(prefix="/agent",tags=["agent"])

class AgentRunRequest(BaseModel):
    query:str=Field(min_length=1,max_length=4000,description="用户输入")
    thread_id:str|None =Field(default=None,description="对话线程ID，缺少则新建")

@agent.post('/runs')
async def create_run(
    data:AgentRunRequest,
    user:User=Depends(get_required_user),
):
    """通过Agent处理一条消息，SSE流式返回"""
    thread_id=data.thread_id or str(uuid.uuid4())

    async def event_generator():
        agent_instance=agent_manager.get_agent("ChatbotAgent")
        messages=[HumanMessage(content=data.query)]
        async for msg,metadata in agent_instance.stream_messages_with_state(
            messages,
            input_context={"uid": user.uid, "thread_id": thread_id},
        ):
            content = getattr(msg,"content","")
            if content:
                yield format_sse({"content":content},"message")
        yield format_sse({"content":"","thread_id":thread_id},"done")

    return StreamingResponse(event_generator(),media_type="text/event-stream")
