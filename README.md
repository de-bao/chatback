# AI Chat Backend

后端AI聊天服务，使用FastAPI和OpenAI API。

## 环境变量配置

**重要：** 敏感信息必须配置在 `.env` 文件中，不要硬编码在代码里！

### 1. 复制环境变量模板

```bash
cp .env.example .env
```

### 2. 编辑 `.env` 文件

```bash
# OpenAI API 配置
OPENAI_API_KEY=your_api_key_here          # 必填：你的API密钥
OPENAI_MODEL=Qwen3-30B-A3B-Instruct-2507-FP8  # 可选：模型名称（有默认值）
OPENAI_BASE_URL=https://your-api-base-url/v1  # 必填：API基础URL

# 数据库配置（可选）
DB_PATH=chat_history.db                    # 可选：数据库文件路径
```

### 3. 必需的环境变量

- `OPENAI_API_KEY`: OpenAI API密钥（**必填**）
- `OPENAI_BASE_URL`: OpenAI API基础URL（**必填**）
- `OPENAI_MODEL`: 使用的模型名称（可选，有默认值）
- `DB_PATH`: SQLite数据库文件路径（可选，默认 `chat_history.db`）

**注意：** 如果缺少必填的环境变量，服务启动时会报错并提示。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行服务

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

服务将在 `http://localhost:8000` 启动。

## API端点

### POST /api/chat

发送聊天消息并获取AI回复。

**请求体：**
```json
{
  "messages": [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！有什么可以帮助你的吗？"},
    {"role": "user", "content": "介绍一下Python"}
  ],
  "model": "Qwen3-30B-A3B-Instruct-2507-FP8"  // 可选
}
```

**响应：**
```json
{
  "role": "assistant",
  "content": "Python是一种高级编程语言..."
}
```

### POST /api/chat/save

保存聊天记录到数据库。

**请求体：**
```json
{
  "session_id": 1,  // 可选，如果提供则更新现有会话
  "name": "聊天标题",
  "messages": [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！"}
  ]
}
```

**响应：**
```json
{
  "session_id": 1,
  "message": "Chat saved successfully"
}
```

### GET /api/chat/sessions

获取所有聊天会话列表。

**响应：**
```json
[
  {
    "id": 1,
    "name": "聊天标题",
    "created_at": "2026-02-13T10:00:00",
    "updated_at": "2026-02-13T10:30:00"
  }
]
```

### GET /api/chat/session/{session_id}

获取指定聊天会话的详细信息。

**响应：**
```json
{
  "id": 1,
  "name": "聊天标题",
  "messages": [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！"}
  ],
  "created_at": "2026-02-13T10:00:00",
  "updated_at": "2026-02-13T10:30:00"
}
```

### DELETE /api/chat/session/{session_id}

删除指定的聊天会话及其所有消息。

**响应：**
```json
{
  "message": "Chat session deleted successfully"
}
```

### GET /health

健康检查端点。

### GET /

根端点，返回API信息。
