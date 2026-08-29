"""工具服务：按context解析要加载的工具"""
from kk.agents.toolkits.registry import get_all_tool_instances

def resolve_runtime_tools(context)->list:
    """
    根据 context.tool 过滤要加载的工具
    - None:加载全部
    - [..]:只加载列表里的工具
    """
    all_tools = get_all_tool_instances()
    by_name={tool.name:tool for tool in all_tools}

    selected = context.tools if context.tools is not None else list(by_name.keys())

    tools = []
    for tool_name in selected:
        tool = by_name.get(tool_name)
        if tool is None:
            continue
        tools.append(tool)
    return tools