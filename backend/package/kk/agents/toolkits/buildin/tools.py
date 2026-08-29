"""内置基础工具"""

from datetime import datetime

from pydantic import BaseModel, Field

from kk.agents.toolkits.registry import tool


class CalculatorInput(BaseModel):
    """计算器参数"""
    a: float = Field(description="第一个操作数")
    b: float = Field(description="第二个操作数")
    operation: str = Field(description="运算类型，取值add/sub/mul/div")


@tool(category="buildin", tags=["计算"], display_name="计算器", args_schema=CalculatorInput)
def calculator(a: float, b: float, operation: str) -> float:
    """进行基础四则运算"""
    if operation == "add":
        return a+b
    if operation == "sub":
        return a-b
    if operation == "mul":
        return a*b
    if operation == "div":
        if b == 0:
            return "Error:除数为零"
        return a/b
    return f"Error:未知运算{operation}"

@tool(category="buildin",tags=["时间"],display_name="获取当前时间")
def get_current_time()->str:
    """获取当前的日期和时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
