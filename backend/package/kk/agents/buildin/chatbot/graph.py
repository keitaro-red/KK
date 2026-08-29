"""ChatbotAgent 实现"""
from __future__ import annotations

from langchain.agents import create_agent

from kk.config import config
from kk.agents.base import BaseAgent
from kk.agents.context import BaseContext
from kk.models.chat import select_model
from kk.agents.toolkits.service import resolve_runtime_tools

from .context import ChatBotContext
from .prompt import build_prompt_with_context

class ChatbotAgent(BaseAgent):
    """基础对话AI"""

    name="智能助手"
    description="基础的对话机器人，可以回答问题"
    context_schema=ChatBotContext

    async def get_graph(self, context:BaseContext|None = None, **kwargs):
        context = context or self.context_schema()

        model_spec = context.model or config.DEFAULT_MODEL
        model = select_model(model_spec).model

        graph = create_agent(
            model=model,
            tools=resolve_runtime_tools(context),       # 工具
            system_prompt=build_prompt_with_context(context),
            middleware=[],      #中间件
            checkpointer=self.checkpointer,
        )
        return graph