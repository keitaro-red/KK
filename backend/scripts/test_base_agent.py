"""临时 验证BaseAgent能否正常输出"""
import asyncio

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from kk.config import config
from kk.agents.base import BaseAgent
from kk.models.chat import select_model


class MinimalAgent(BaseAgent):
    """最小可以Agent，只做纯回答"""

    async def get_graph(self, context=None):
        model_spec = context.model or config.DEFAULT_MODEL
        model = select_model(model_spec).model
        return create_agent(
            model=model,
            system_prompt=context.system_prompt,
            checkpointer=self.checkpointer,
        )


async def main():
    agent = MinimalAgent()
    messages = [HumanMessage(content="简单介绍一下你自己")]
    print('='*20, "默认 prompt ", '='*20)
    async for msg, metadata in agent.stream_messages_with_state(messages):
        content = getattr(msg, "content", "")
        if content:
            print(content, end="", flush=True)
    print()

    print('='*20, "鲁迅风格 prompt", '='*20)
    async for msg, _ in agent.stream_messages_with_state(
        messages,
        input_context={"system_prompt": "用鲁迅的文风来回答", "nonexistent_field": 123}
    ):
        content = getattr(msg, "content", "")
        if content:
            print(content, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(main())
