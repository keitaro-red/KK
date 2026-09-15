"""Agent Run 表（未拓展）"""
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text, Integer

from kk.models.user import Base

TERMINAL_RUN_STATUSES = {"completed", "failed", "cancelled", "interrupted"}


class AgentRun(Base):
    """一次Agent 执行任务"""

    __tablename__ = "agent_runs"

    id = Column(String(64), primary_key=True, comment="run_id(UUID)")
    thread_id = Column(String(64), index=True,
                       nullable=False, comment="对话线程 ID")
    uid = Column(String(64), index=True, nullable=False, comment="用户ID")
    agent_slug = Column(String(64), nullable=False, comment="Agent 标识")
    run_type = Column(String(20), nullable=False, default="chat",
                      comment="chat普通对话/resume恢复interrupted")
    input_message_id = Column(Integer, nullable=True,
                              comment="输入消息ID(指向Message.id)")
    status = Column(String(20), nullable=False, default="pending",
                    comment="pending/running/completed/failed")
    error_type = Column(String(64), nullable=True, comment="错误类型")
    error_message = Column(Text, nullable=True, comment="错误详情")
    created_at = Column(DateTime, default=datetime.utcnow())
    started_at = Column(DateTime, nullable=True, comment="开始执行时间")
    finished_at = Column(DateTime, nullable=True, comment="结束时间")
    updated_at = Column(DateTime, default=datetime.utcnow(),
                        onupdate=datetime.utcnow())
