"""Agent 基类：统一的图构建与流式调用接口"""
from __future__ import annotations

from abc import abstractmethod
from typing import Any, AsyncIterator

from langchain_core.messages import AnyMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph
from langchain.agents import create_agent

from kk.agents.context import BaseContext
from kk.storage.postgres.checkpointer import get_checkpointer


class BaseAgent:
    """Agent基类"""
    name = "base_agent"
    description = "base_agent"
    context_schema = BaseContext

    def __init__(self):
        self.graph: CompiledStateGraph | None = None
        # self.checkpointer = InMemorySaver()

    async def get_config(self) -> BaseContext:
        """返回一份默认配置"""
        return self.context_schema()

    @abstractmethod
    async def get_graph(self,context:BaseContext|None=None, **kwargs) -> CompiledStateGraph:
        """
        编译LangGraph图
        编译时必须绑定 self.checkpointer
        否则无法恢复多轮对话状态
        图构建时从context 读取model/system_prompt等配置
        """
        checkpointer = await get_checkpointer()
        graph = create_agent(...,checkpointer=checkpointer)
        return graph

    async def stream_messages_with_state(
        self,
        messages: list[AnyMessage],
        input_context: dict | None = None,
        graph_input: dict | None = None,
        **kwargs,
    ) -> AsyncIterator[tuple[AnyMessage, dict]]:
        """流式执行图，逐条产出(message,metadata)"""
        # 配置context
        context = self.context_schema()
        context.update_from_dict(input_context or {})
        # context注入图
        graph = await self.get_graph(context=context,**kwargs)
        # 配置config
        config = {"configurable": {"thread_id": context.thread_id,"uid":context.uid}}
        payload = graph_input if graph_input is not None else {"messages":messages or []}
        async for msg, metadata in graph.astream(
            payload,
            stream_mode="messages",
            config=config,
        ):
            yield msg, metadata

    async def invoke_messages(
        self,
        messages: list[AnyMessage],
        input_context: dict | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """非流式执行图，一次性返回state"""
        context = self.context_schema
        context.update_from_dict(input_context or {})
        graph = await self.get_graph(context=context,**kwargs)
        config = {"configurable": {"thread_id": context.thread_id,"uid":context.uid}}
        return await graph.ainvoke(
            {"messages": messages},
            config=config,
        )

    async def get_pending_interrupt(self,input_context:dict|None=None,**kwargs):
        """
        查询这次run是否挂在中断上
        返回中断载荷列表；没有中断返回空列表
        """

        context = self.context_schema()
        context.update_from_dict(input_context or {})
        graph = await self.get_graph(context=context,**kwargs)
        config = {"configurable": {"thread_id": context.thread_id,"uid":context.uid}}
        snapshot = await graph.aget_state(config)
        return list(snapshot.interrupts or ())

    