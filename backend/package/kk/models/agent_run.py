"""Agent Run 表（未拓展）"""
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text

from kk.models.user import Base


class AgentRun(Base):
    """一次Agent 执行任务"""

    __tablename__ = "agent_runs"

    id = Column(String(64), primary_key=True, comment="run_id(UUID)")
    thread_id = Column(String(64), index=True,
                       nullable=False, comment="对话线程 ID")
    uid = Column(String(64), index=True, nullable=False, comment="用户ID")
    agent_slug = Column(String(64), nullable=False, comment="Agent 标识")
    query = Column(Text, nullable=False, comment="用户输入")
    status = Column(String(20), nullable=False, default="pending",
                    comment="pending/running/completed/failed")
    error_message = Column(Text, nullable=True, comment="失败原因")
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow(),
                        onupdate=datetime.utcnow())
