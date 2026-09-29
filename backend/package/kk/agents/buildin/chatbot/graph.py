"""ChatbotAgent 实现"""
from __future__ import annotations

from langchain.agents import create_agent
from langchain.agents.middleware import ModelRetryMiddleware

from kk.config import config
from kk.agents.base import BaseAgent
from kk.agents.context import BaseContext
from kk.models.chat import select_model
from kk.agents.toolkits.service import resolve_runtime_tools
from kk.agents.middlewares.attachment import AttachmentMiddleware
from kk.agents.middlewares.summary import create_summary_middleware
from kk.agents.middlewares.token_usage import TokenUsageMiddleware
from kk.agents.tool_approval import create_tool_approval_middleware, normalize_tool_approval_mode
from kk.storage.postgres.checkpointer import get_checkpointer

from .context import ChatBotContext
from .prompt import build_prompt_with_context


async def _build_middleware(context: BaseContext):
    """构建中间件"""
    middlewares = [
        AttachmentMiddleware(),                 # 附件
        create_summary_middleware(context),     # 压缩
        ModelRetryMiddleware(max_retries=context.model_retry_times),    # 重试
        TokenUsageMiddleware(),         # 统计
    ]
    approval = create_tool_approval_middleware(
        normalize_tool_approval_mode(
            getattr(context, "tool_approval_mode", "default")),
    )
    if approval:
        middlewares.append(approval)
    return middlewares


class ChatbotAgent(BaseAgent):
    """基础对话AI"""

    name = "智能助手"
    description = "基础的对话机器人，可以回答问题"
    context_schema = ChatBotContext

    async def get_graph(self, context: BaseContext | None = None, **kwargs):
        context = context or self.context_schema()

        model_spec = context.model or config.DEFAULT_MODEL
        model = select_model(model_spec).model

        graph = create_agent(
            model=model,
            tools=resolve_runtime_tools(context),       # 工具
            system_prompt=build_prompt_with_context(context),
            middleware=await _build_middleware(context),  # 中间件
            checkpointer=await get_checkpointer(),
        )
        return graph
