"""对话和消息模型"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from kk.models.user import Base


class Conversation(Base):
    """对话线程"""

    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(String(64), unique=True,
                       index=True, nullable=False)  # UUID
    uid = Column(String(64), index=True, nullable=False)  # 用户uid
    agent_id = Column(String(64), nullable=True)       # 预备
    title = Column(String(255), default="新的对话")     #标题
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """对话消息"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey(
        "conversations.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 角色
    content = Column(Text, nullable=False)  # 内容
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")
