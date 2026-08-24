"""Agent 基类：统一的图构建与流式调用接口"""
from __future__ import annotations

from abc import abstractmethod
from typing import Any, AsyncIterator

from langchain_core.messages import AnyMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph


class BaseAgent:
    """Agent基类"""
    name = "base_agent"
    description = "base_agent"

    def __init__(self):
        self.graph: CompiledStateGraph | None = None
        self.checkpointer = InMemorySaver()

    @abstractmethod
    async def get_graph(self, **kwargs) -> CompiledStateGraph:
        """
        编译LangGraph图
        编译时必须绑定 self.checkpointer
        否则无法恢复多轮对话状态
        """
        ...

    async def stream_messages_with_state(
        self,
        messages: list[AnyMessage],
        thread_id: str | None = None,
        **kwargs,
    ) -> AsyncIterator[tuple[AnyMessage, dict]]:
        """流式执行图，逐条产出(message,metadata)"""
        graph = await self.get_graph(**kwargs)
        config = {"configurable": {"thread_id": thread_id}}
        async for msg, metadata in graph.astream(
            {"messages": messages},
            stream_mode="messages",
            config=config,
        ):
            yield msg, metadata

    async def invoke_messages(
        self,
        messages: list[AnyMessage],
        thread_id: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """非流式执行图，一次性返回state"""
        graph = await self.get_graph(**kwargs)
        config = {"configurable": {"thread_id": thread_id}}
        return await graph.ainvoke(
            {"messages": messages},
            config=config,
        )
