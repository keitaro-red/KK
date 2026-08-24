"""Agent 共享状态定义"""
from typing import Annotated

from langchain.agents import AgentState


def merge_artifacts(existing: list[str] | None, new: list[str] | None) -> list[str]:
    """合并交付物的文件路径，保序去重"""
    if existing is None:
        return new or []
    if new is None:
        return existing
    return list(dict.fromkeys(existing+new))


class BaseState(AgentState):
    """KK Agent共享状态"""
    artifacts: Annotated[list[str], merge_artifacts]
    
