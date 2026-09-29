"""工具审批中间件"""
from langchain.agents.middleware import HumanInTheLoopMiddleware

# 默认审批下拦截的敏感工具列表
SENSITIVE_BACKEND_TOOLS = frozenset({"write_file","edit_file","execute"})

TOOL_APPROVAL_INTERRUPT_ON = {
    tool_name:{"allowed_decisions":["approve","reject"]}
    for tool_name in SENSITIVE_BACKEND_TOOLS
}


def normalize_tool_approval_mode(mode)->str:
    """规范化审批模式，"""
    value = mode.strip() if isinstance(mode,str) else mode
    if value not in {"default","always_trust"}:
        raise ValueError(f"不支持的 tool_approval_mode：{mode}")
    return value

def create_tool_approval_middleware(mode:str):
    """构建 mode 审批模式的中间件"""
    mode = normalize_tool_approval_mode(mode)
    if mode == "always_trust":
        return None
    return HumanInTheLoopMiddleware(interrupt_on=TOOL_APPROVAL_INTERRUPT_ON)