"""
认证相关工具函数
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models import User
from database import get_db
import os
from dotenv import load_dotenv

load_dotenv()

# 北京时间（UTC+8）
BEIJING_TZ = timezone(timedelta(hours=8))

def beijing_now():
    """获取当前北京时间"""
    return datetime.now(BEIJING_TZ)

# JWT配置
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "12345678")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24 * 365  # 365天

# 启动时打印JWT配置（用于调试）
print(f"🔐 [JWT配置] SECRET_KEY: {JWT_SECRET_KEY[:20]}... (长度: {len(JWT_SECRET_KEY)})")

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """加密密码"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = beijing_now() + expires_delta
    else:
        expire = beijing_now() + timedelta(hours=JWT_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """验证JWT token"""
    if not token:
        print(f"❌ [Token验证失败] token为空")
        return None
    try:
        print(f"🔍 [verify_token] 开始验证token: {token[:50]}...")
        print(f"🔍 [verify_token] 使用SECRET_KEY: {JWT_SECRET_KEY[:20]}... (长度: {len(JWT_SECRET_KEY)})")
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        print(f"✅ [verify_token] token验证成功: {payload}")
        return payload
    except JWTError as e:
        print(f"❌ [Token验证失败] JWTError: {str(e)}, SECRET_KEY: {JWT_SECRET_KEY[:20]}...")
        return None
    except Exception as e:
        print(f"❌ [Token验证失败] 其他错误: {type(e).__name__}: {str(e)}")
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    print(f"🔍 [Token验证] 收到token: {token[:50]}...")
    print(f"🔍 [Token验证] JWT_SECRET_KEY: {JWT_SECRET_KEY[:20]}...")
    
    payload = verify_token(token)
    if payload is None:
        print(f"❌ [Token验证] verify_token返回None")
        raise credentials_exception
    
    print(f"✅ [Token验证] payload: {payload}")
    
    user_id_str = payload.get("sub")
    if user_id_str is None:
        print(f"❌ [Token验证] payload中没有sub字段")
        raise credentials_exception
    
    # sub是字符串，需要转换为整数
    try:
        user_id = int(user_id_str)
        print(f"🔍 [Token验证] user_id: {user_id} (从字符串 '{user_id_str}' 转换)")
    except (ValueError, TypeError):
        print(f"❌ [Token验证] user_id转换失败: {user_id_str}")
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        print(f"❌ [Token验证] 用户不存在: user_id={user_id}")
        raise credentials_exception
    
    print(f"✅ [Token验证] 用户验证成功: {user.username}")
    return user
