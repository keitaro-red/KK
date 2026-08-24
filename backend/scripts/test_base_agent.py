"""临时 验证BaseAgent能否正常输出"""
import asyncio

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from kk.config import config
from kk.agents.base import BaseAgent
from kk.models.chat import select_model

class MinimalAgent(BaseAgent):
    """最小可以Agent，只做纯回答"""
    async def get_graph(self):
        model = select_model(config.DEFAULT_MODEL).model
        return create_agent(
            model=model,
            system_prompt="你是一个简洁助手",
            checkpointer=self.checkpointer,
        )

async def main():
    agent = MinimalAgent()
    messages = [HumanMessage(content="1+1=?")]
    async for msg,metadata in agent.stream_messages_with_state(messages):
        content = getattr(msg,"content","")
        if content:
            print(content,end="",flush=True)
        print()

if __name__ =="__main__":
    asyncio.run(main())