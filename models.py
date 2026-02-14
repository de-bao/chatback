from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class ChatSession(Base):
    __tablename__ = 'chat_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
