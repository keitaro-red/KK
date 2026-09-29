"""Token 统计中间件"""

from langchain.agents.middleware import AgentMiddleware
from langchain.agents.middleware.types import ExtendedModelResponse
from langchain_core.messages.utils import count_tokens_approximately
from langgraph.types import Command

class TokenUsageMiddleware(AgentMiddleware):
    """每次模型调用，估计并且记录 state 的 token 的消耗"""

    async def awrap_model_call(self, request, handler):
        response = await handler(request)

        state_messages = request.state.get("messages",[])
        total_tokens = count_tokens_approximately(state_messages)

        snapshot = {
            "state_message_count":len(state_messages),
            "state_message_tokens":total_tokens,
        }   # 记录 state 的 token 消耗
        print("[token_usage]", snapshot, flush=True) # 调试用

        return ExtendedModelResponse(
            model_response=response,
            command=Command(update={"token_usage":snapshot}),
        )