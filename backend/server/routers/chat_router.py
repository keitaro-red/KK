"""模型对话路由"""
from fastapi import APIRouter,Depends
from pydantic import BaseModel,Field

from kk.config import config
from kk.models.chat import select_model
from kk.models.user import User
from server.utils.auth_middleware import get_required_user

chat = APIRouter(prefix="/chat",tags=["chat"])

class ChatCallRequest(BaseModel):
    query:str = Field(min_length=1,max_length=4000,description="用户输入")

class ChatCallResponse(BaseModel):
    response:str

@chat.post("/call",response_model=ChatCallResponse)
async def call_llm(
    data:ChatCallRequest,
    user:User=Depends(get_required_user),
):
    """非流式调用LLM，一次性返回完整回复"""
    adapter = select_model(config.DEFAULT_MODEL)
    reply = await adapter.call(data.query)
    return ChatCallResponse(response=reply)

from fastapi.responses import StreamingResponse
from kk.utils.sse_utils import format_sse

@chat.post("/stream",tags=["stream"])
async def stream_llm(
    data:ChatCallRequest,
    user:User = Depends(get_required_user),
):
    """流式调用LLM，逐个token返回"""
    async def event_generator():
        adapter = select_model(config.DEFAULT_MODEL)
        async for token in adapter.stream(data.query):
            yield format_sse({"content":token},"message")
        yield format_sse({"content":""},"done")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )