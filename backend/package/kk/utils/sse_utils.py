"""SSE格式化工具"""
import json


def format_sse(data: dict, event: str) -> str:
    """把数据格式化成SSE事件"""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
