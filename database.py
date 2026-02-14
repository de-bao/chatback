from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# SQLite数据库路径（从环境变量读取，无默认值）
DB_PATH = os.getenv('DB_PATH')
if not DB_PATH:
    raise ValueError("DB_PATH 环境变量未设置，请在 .env 文件中配置")

engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
