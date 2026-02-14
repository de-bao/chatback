from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy.orm import Session
from models import ChatSession, ChatMessage
from database import get_db, init_db

# 加载环境变量（必须在导入 database 之前）
load_dotenv()

# 从环境变量获取所有配置（必须配置，无默认值）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
CORS_ORIGINS_STR = os.getenv("CORS_ORIGINS")

# 验证必需的配置
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY 环境变量未设置，请在 .env 文件中配置")
if not OPENAI_MODEL:
    raise ValueError("OPENAI_MODEL 环境变量未设置，请在 .env 文件中配置")
if not OPENAI_BASE_URL:
    raise ValueError("OPENAI_BASE_URL 环境变量未设置，请在 .env 文件中配置")
if not CORS_ORIGINS_STR:
    raise ValueError("CORS_ORIGINS 环境变量未设置，请在 .env 文件中配置")

# 解析配置值
CORS_ORIGINS = CORS_ORIGINS_STR.split(",") if CORS_ORIGINS_STR != "*" else ["*"]

# 初始化数据库（在创建 app 之前）
init_db()

app = FastAPI(title="AI Chat API", version="1.0.0")

# 配置CORS，允许前端跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化OpenAI客户端（按照阿里云百炼示例，使用默认配置）
# 阿里云百炼使用标准 HTTPS，不需要特殊配置
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL
)


# 请求和响应模型
class Message(BaseModel):
    role: str  # 'user' 或 'assistant'
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = None  # 可选，如果不提供则使用默认模型


class ChatResponse(BaseModel):
    role: str
    content: str


# 数据库相关的请求和响应模型
class SaveChatRequest(BaseModel):
    session_id: Optional[int] = None
    name: str
    messages: List[dict]  # [{role: str, content: str}]


class ChatSessionResponse(BaseModel):
    id: int
    name: str
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


@app.get("/")
async def root():
    return {"message": "AI Chat API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    聊天API端点
    接收消息列表，返回AI回复
    """
    try:
        # 验证消息列表不为空
        if not request.messages:
            raise HTTPException(status_code=400, detail="Messages list cannot be empty")
        
        # 使用请求中的模型或默认模型
        model = request.model or OPENAI_MODEL
        
        # 转换消息格式为OpenAI API格式
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        # 调用OpenAI API（阿里云百炼兼容 OpenAI API）
        # 使用 run_in_executor 在异步环境中执行同步调用
        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model=model,
                messages=messages,
                stream=False
            )
        )
        
        # 提取回复内容
        if not response.choices or not response.choices[0].message:
            raise HTTPException(status_code=500, detail="Empty response from OpenAI API")
        
        assistant_message = response.choices[0].message.content
        
        if assistant_message is None:
            assistant_message = ""
        
        return ChatResponse(
            role="assistant",
            content=assistant_message
        )
    
    except HTTPException:
        raise
    except Exception as e:
        # 打印详细错误信息用于调试
        import traceback
        error_detail = str(e)
        error_trace = traceback.format_exc()
        print(f"OpenAI API Error: {error_detail}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Error calling OpenAI API: {error_detail}")


# ==================== 数据库持久化 API ====================

@app.post("/api/chat/save")
async def save_chat(request: SaveChatRequest, db: Session = Depends(get_db)):
    """保存聊天记录"""
    try:
        if request.session_id:
            # 更新现有会话
            session = db.query(ChatSession).filter_by(id=request.session_id).first()
            if not session:
                raise HTTPException(status_code=404, detail="Chat session not found")
            session.name = request.name
        else:
            # 创建新会话
            session = ChatSession(name=request.name)
            db.add(session)
            db.flush()
        
        # 删除旧消息
        db.query(ChatMessage).filter_by(session_id=session.id).delete()
        
        # 添加新消息
        for msg in request.messages:
            message = ChatMessage(
                session_id=session.id,
                role=msg['role'],
                content=msg['content']
            )
            db.add(message)
        
        db.commit()
        return {"session_id": session.id, "message": "Chat saved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving chat: {str(e)}")


@app.get("/api/chat/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(db: Session = Depends(get_db)):
    """获取所有聊天会话"""
    try:
        sessions = db.query(ChatSession).order_by(ChatSession.updated_at.desc()).all()
        return [
            ChatSessionResponse(
                id=session.id,
                name=session.name,
                created_at=session.created_at.isoformat(),
                updated_at=session.updated_at.isoformat()
            )
            for session in sessions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chat sessions: {str(e)}")


@app.get("/api/chat/session/{session_id}")
async def get_chat_session(session_id: int, db: Session = Depends(get_db)):
    """获取聊天会话详情"""
    try:
        session = db.query(ChatSession).filter_by(id=session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        messages = db.query(ChatMessage).filter_by(session_id=session_id).order_by(ChatMessage.created_at).all()
        
        return {
            "id": session.id,
            "name": session.name,
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ],
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chat session: {str(e)}")


@app.delete("/api/chat/session/{session_id}")
async def delete_chat_session(session_id: int, db: Session = Depends(get_db)):
    """删除聊天会话"""
    try:
        session = db.query(ChatSession).filter_by(id=session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # 删除关联消息
        db.query(ChatMessage).filter_by(session_id=session_id).delete()
        # 删除会话
        db.delete(session)
        db.commit()
        
        return {"message": "Chat session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting chat session: {str(e)}")
