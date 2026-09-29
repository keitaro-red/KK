"""用户模型"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    """用户模型"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True,)
    username = Column(String(50), unique=True, index=True, nullable=False)  # 用户名
    uid = Column(String(64), nullable=False, unique=True, index=True)  # uid
    password_hash = Column(String(255), nullable=False)  # 密码哈希
    role = Column(String(20), nullable=False, default="user")  # user/admin
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User(id='{self.id}',uid='{self.uid}',role='{self.role}')>"
