"""KK Agent运行上下文配置"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field


@dataclass(kw_only=True)
class BaseContext:
    """
    Agent 配置基类
    配置优先级：
    1. 运行时传入（input_context 字典覆盖）
    2. 类默认值
    """

    # 身份字段（运行时注入，不可配置）
    thread_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    uid: str = field(default_factory=lambda: str(uuid.uuid4()))

    # 核心配置（用户可配置）
    system_prompt: str = "You are a helpful assistant."
    model: str = ""          # 留空使用系统默认

    #  调优参数（后续接入）
    tools: list[str] | None = None  # None表示启用全部工具
    max_excution_steps: int = 300   
    model_retry_times: int = 2
    summary_threshold: int = 100  # 单位：K token
    summary_keep_messages: int = 10
    tool_approval_mode: str = "default"

    def update_from_dict(self, data: dict) -> None:
        """用字典覆盖已有字段（多余的字段忽略）"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
