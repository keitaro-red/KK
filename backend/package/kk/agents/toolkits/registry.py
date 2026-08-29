"""工具装饰器与注册表"""
from dataclasses import dataclass,field
from typing import Callable

from langchain.tools import tool as langchain_tool

@dataclass
class ToolExtraMetadata:
    """工具的附加元数据（装饰器注册）"""

    category:str = "" # 分类：buildin / filesystem /...
    tags:list[str]=field(default_factory=list)
    display_name:str = ""       #名字

# 全局注册表：工具->元数据
_extra_registry :dict[str,ToolExtraMetadata]={}

# 全局工具实例表（@tool 装饰器自动收集） 
_all_tool_instances:list = []

def get_all_tool_instances()->list:
    """获取全部工具实例"""
    return _all_tool_instances

def get_extra_metadata(tool_name:str)->ToolExtraMetadata|None:
    """获取某一工具的元数据，无返回None"""
    return _extra_registry.get(tool_name)

def tool(
    category:str="",        # 分类 buildin/filesystem/knowledge
    tags:list[str]|None=None,       # 前端筛选
    display_name:str="",            # 名称
    description:str|None=None,
    args_schema:type|None=None,
    return_direct:bool=False,
):
    """
    包装langchain.tool，同时注册附加元数据
    用法：
    @tool(category="buildin",display_name="计算器")
    def calculator(a:float,b:float,operation:str)->float:...
    """
    langchain_decorator=langchain_tool(
        description=description,
        args_schema=args_schema,
        return_direct=return_direct,
    )

    def decorator(func:Callable)->Callable:
        tool_obj = langchain_decorator(func)
        tool_name = tool_obj.name
        _extra_registry[tool_name]=ToolExtraMetadata(
            category=category,
            tags= tags or [],
            display_name=display_name,
        )
        _all_tool_instances.append(tool_obj)
        return tool_obj

    return decorator

    