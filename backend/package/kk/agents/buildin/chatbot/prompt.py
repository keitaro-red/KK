"""ChatbotAgent 系统提示词"""
from datetime import datetime

PROMPT= """\
你是一个智能助手"KK"，专门回答用户问题。
请根据用户提供的信息尽可能简洁明了地回答，不确定时说不知道。
保持专业，回答用Markdown格式。
"""

def build_prompt_with_context(context)->str:
    """把日期 + 固定角色 + 用户自定义提示词拼接成最终system_prompt"""
    current_date = f"当前日期：{datetime.now().strftime('%Y-%m-%d')}"
    return f"{current_date}\n\n{PROMPT.strip()}\n\n{context.system_prompt or ''}".strip()