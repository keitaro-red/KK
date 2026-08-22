"""对话仓库"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kk.models.conversation import Conversation, Message


class ConversationRepository:
    """对话域持久化操作"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_conversation(self, uid: str, title: str | None = None) -> Conversation:
        """创建对话"""
        conversation = Conversation(
            thread_id=str(uuid.uuid4()),
            uid=uid,
            title=title or "新的对话",
        )
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def get_conversation_by_thread_id(self,thread_id:str)->Conversation|None:
        """根据uuid返回对应对话"""
        result = await self.db.execute(
            select(Conversation).where(Conversation.thread_id==thread_id)
        )
        return result.scalar_one_or_none()

    async def list_conversations(self, uid: str) -> list[Conversation]:
        """返回对应uid的全部对话"""
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.uid == uid)
            .order_by(Conversation.updated_at.desc())
        )
        return list(result.scalars().all())

    async def add_message(self,thread_id:str,role:str,content:str)->Message|None:
        """添加消息"""
        conversation = await self.get_conversation_by_thread_id(thread_id)
        if not conversation:
            return None
        message = Message(
            conversation_id=conversation.id,
            role=role,
            content=content,
            )
        self.db.add(message)
        await  self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_message_by_thread_id(self,thread_id:str)->list[Message]:
        """根据uuid返回对话的全部消息"""
        conversation = await self.get_conversation_by_thread_id(thread_id)
        if not conversation:
            return []
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id==conversation.id)
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())
