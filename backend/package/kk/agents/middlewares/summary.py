"""上下文压缩中间件 未完全版"""


from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import ToolMessage
from langchain_core.messages.utils import count_tokens_approximately

APPROX_CHARS_PER_ROKEN = 4


class SummarizationMiddleware(AgentMiddleware):
    """
    截断过长的工具结果

    """

    def __init__(self, trigger_tokens: int = 100_000, tool_result_token_limit: int = 300):
        self.trigger_tokens = trigger_tokens
        self.tool_result_token_limit = tool_result_token_limit

    async def awrap_model_call(self, request, handler):
        messages = list(request.messages)
        total_tokens = count_tokens_approximately(messages)

        if total_tokens <= self.trigger_tokens:
            return await handler(request)   # 未超过阈值，直接放行

        # 超过阈值，截断过长工具结果
        truncated = self._truncate_tool_result(messages)
        request = request.override(messages=truncated)

        return await handler(request)

    def _truncate_tool_result(self, messages):
        """把超过 token 上限的 ToolMessage 内容截断"""
        print(f"[summary] 截断 ToolMessage：{len(messages)} 字符", flush=True)
        result = []
        max_chars = self.tool_result_token_limit * APPROX_CHARS_PER_ROKEN
        for msg in messages:
            if isinstance(msg, ToolMessage):
                content = msg.content if isinstance(
                    msg.content, str) else str(msg.content)
                if len(content) > max_chars:
                    preview = content[:max_chars]
                    msg = msg.model_copy(
                        update={"content": f"{preview}\n[截断，共{len(content)}字符]"})
            result.append(msg)
        return result


def create_summary_middleware(context) -> SummarizationMiddleware:
    """根据 context 构建压缩中间件"""
    trigger_tokens = getattr(context, "summary_threshold", 100) *1024
    tool_limit = 300
    return SummarizationMiddleware(
        trigger_tokens=trigger_tokens,
        tool_result_token_limit=tool_limit,
    )