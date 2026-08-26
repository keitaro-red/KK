"""ChatbotAgent 配置"""
from __future__ import annotations
from dataclasses import dataclass,field

from kk.agents.context import BaseContext

@dataclass(kw_only=True)
class ChatBotContext(BaseContext):
    """ChatBotAgent 专属配置
    加了subagents"""

    subagents:list[str]|None=None   