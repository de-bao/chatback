from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import asyncio
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy.orm import Session
from models import User, ChatSession, ChatMessage
from database import get_db, init_db
from auth import (
    get_current_user, 
    verify_password, 
    get_password_hash, 
    create_access_token
)
from fastapi.security import OAuth2PasswordRequestForm

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

# 添加启动日志
import os
import time
db_path = os.getenv('DB_PATH', 'unknown')
abs_path = os.path.abspath(db_path) if db_path != 'unknown' else 'unknown'
print(f"🚀 [启动] 数据库路径: {abs_path}")
if os.path.exists(abs_path):
    file_stat = os.stat(abs_path)
    mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stat.st_mtime))
    print(f"🚀 [启动] 数据库文件大小: {file_stat.st_size} 字节, 最后修改: {mtime}")
else:
    print(f"⚠️ [启动] 数据库文件不存在，将在首次使用时创建: {abs_path}")

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


# 认证相关的请求和响应模型
class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: str
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


@app.get("/")
async def root():
    return {"message": "AI Chat API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


# ==================== 认证 API ====================

@app.post("/api/auth/register", response_model=UserResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    try:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        # 检查邮箱是否已存在
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="邮箱已被注册")
        
        # 创建新用户
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            password=user_data.password  # 同时存储明文密码
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ [注册成功] 用户名: {new_user.username}, 邮箱: {new_user.email}")
        
        return UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            created_at=new_user.created_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ [注册错误] {str(e)}")
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录"""
    try:
        # 查找用户（OAuth2PasswordRequestForm 使用 username 字段）
        user = db.query(User).filter(User.username == form_data.username).first()
        
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 创建token（sub必须是字符串）
        access_token = create_access_token(data={"sub": str(user.id)})
        
        print(f"✅ [登录成功] 用户名: {user.username}, 用户ID: {user.id}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                created_at=user.created_at.isoformat()
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [登录错误] {str(e)}")
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    print(f"✅ [get_current_user_info] 成功获取用户: {current_user.username}")
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at.isoformat()
    )


@app.post("/api/chat")
async def chat(request: ChatRequest, current_user: User = Depends(get_current_user)):
    """
    聊天API端点
    接收消息列表，返回AI回复（流式输出）
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
        
        # 直接返回流式输出
        return StreamingResponse(
            stream_chat_response(model, messages),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # 禁用 Nginx 缓冲
            }
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


async def stream_chat_response(model: str, messages: List[dict]):
    """
    流式输出生成器
    返回 SSE 格式的数据流
    """
    import queue
    import threading
    
    try:
        # 创建一个队列用于在后台线程和异步生成器之间传递数据
        chunk_queue = queue.Queue()
        error_queue = queue.Queue()
        done_event = threading.Event()
        
        def iterate_stream():
            """在后台线程中迭代流式响应"""
            try:
                stream = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True
                )
                
                for chunk in stream:
                    chunk_queue.put(chunk)
                
                # 标记完成
                done_event.set()
            except Exception as e:
                error_queue.put(e)
                done_event.set()
        
        # 在后台线程中启动迭代
        thread = threading.Thread(target=iterate_stream, daemon=True)
        thread.start()
        
        # 异步生成 SSE 格式的数据
        while True:
            # 检查是否有错误
            try:
                error = error_queue.get_nowait()
                raise error
            except queue.Empty:
                pass
            
            # 检查是否有新的 chunk
            try:
                chunk = chunk_queue.get(timeout=0.1)
                
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    
                    # 构建符合 OpenAI 格式的响应
                    response_data = {
                        "choices": [{
                            "delta": {
                                "content": delta.content if hasattr(delta, 'content') and delta.content else "",
                                "role": delta.role if hasattr(delta, 'role') and delta.role else "assistant"
                            }
                        }]
                    }
                    
                    # 发送 SSE 格式的数据
                    yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"
                    
            except queue.Empty:
                # 如果队列为空且已完成，退出循环
                if done_event.is_set():
                    # 再次检查是否有剩余的数据
                    try:
                        while True:
                            chunk = chunk_queue.get_nowait()
                            if chunk.choices and len(chunk.choices) > 0:
                                delta = chunk.choices[0].delta
                                response_data = {
                                    "choices": [{
                                        "delta": {
                                            "content": delta.content if hasattr(delta, 'content') and delta.content else "",
                                            "role": delta.role if hasattr(delta, 'role') and delta.role else "assistant"
                                        }
                                    }]
                                }
                                yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"
                    except queue.Empty:
                        break
                else:
                    # 等待一小段时间后继续检查
                    await asyncio.sleep(0.01)
                    continue
        
        # 发送结束标记
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        # 发送错误信息
        import traceback
        error_detail = str(e)
        error_trace = traceback.format_exc()
        print(f"Stream Error: {error_detail}")
        print(f"Traceback: {error_trace}")
        
        error_data = {
            "error": {
                "message": error_detail,
                "type": type(e).__name__
            }
        }
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"


# ==================== 数据库持久化 API ====================

@app.post("/api/chat/save")
async def save_chat(
    request: SaveChatRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """保存聊天记录"""
    try:
        if request.session_id:
            # 更新现有会话
            session = db.query(ChatSession).filter_by(
                id=request.session_id,
                user_id=current_user.id
            ).first()
            if not session:
                raise HTTPException(status_code=404, detail="Chat session not found")
            session.name = request.name
        else:
            # 创建新会话
            session = ChatSession(name=request.name, user_id=current_user.id)
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
        
        # 添加调试日志
        import os
        import time
        db_path = os.getenv('DB_PATH', 'unknown')
        abs_path = os.path.abspath(db_path) if db_path != 'unknown' else 'unknown'
        print(f"💾 [保存成功] 会话ID: {session.id}, 数据库路径: {abs_path}")
        if os.path.exists(abs_path):
            file_stat = os.stat(abs_path)
            mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stat.st_mtime))
            print(f"💾 [保存成功] 文件大小: {file_stat.st_size} 字节, 最后修改: {mtime}")
        else:
            print(f"⚠️ [警告] 数据库文件不存在: {abs_path}")
        
        return {"session_id": session.id, "message": "Chat saved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving chat: {str(e)}")


@app.get("/api/chat/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的所有聊天会话"""
    try:
        sessions = db.query(ChatSession).filter_by(
            user_id=current_user.id
        ).order_by(ChatSession.updated_at.desc()).all()
        
        # 添加调试日志
        import os
        db_path = os.getenv('DB_PATH', 'unknown')
        abs_path = os.path.abspath(db_path) if db_path != 'unknown' else 'unknown'
        print(f"🔍 [获取会话] 查询到 {len(sessions)} 个会话, 数据库路径: {abs_path}")
        for session in sessions:
            print(f"  - ID: {session.id}, 名称: {session.name}, 更新: {session.updated_at}")
        
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
        print(f"❌ [获取会话错误] {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching chat sessions: {str(e)}")


@app.get("/api/chat/session/{session_id}")
async def get_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取聊天会话详情"""
    try:
        session = db.query(ChatSession).filter_by(
            id=session_id,
            user_id=current_user.id
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        messages = db.query(ChatMessage).filter_by(session_id=session_id).order_by(ChatMessage.created_at).all()
        
        # 添加调试日志
        print(f"🔍 [获取会话详情] 会话ID: {session_id}, 消息数量: {len(messages)}")
        
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
        print(f"❌ [获取会话详情错误] 会话ID: {session_id}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching chat session: {str(e)}")


@app.delete("/api/chat/session/{session_id}")
async def delete_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除聊天会话"""
    try:
        session = db.query(ChatSession).filter_by(
            id=session_id,
            user_id=current_user.id
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # 删除关联消息
        db.query(ChatMessage).filter_by(session_id=session_id).delete()
        # 删除会话
        db.delete(session)
        db.commit()
        
        # 添加调试日志
        print(f"🗑️ [删除会话] 会话ID: {session_id}, 名称: {session.name}")
        
        return {"message": "Chat session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ [删除会话错误] 会话ID: {session_id}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting chat session: {str(e)}")
