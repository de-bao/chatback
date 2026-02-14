# AI Chat Backend

后端AI聊天服务，使用 FastAPI 和 OpenAI API（兼容阿里云百炼），支持聊天历史持久化。

## ✨ 特性

- ✅ FastAPI 框架，高性能异步处理
- ✅ SQLite 数据库持久化聊天历史
- ✅ 支持 OpenAI 兼容 API（阿里云百炼等）
- ✅ RESTful API 设计
- ✅ CORS 跨域支持

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件（项目根目录已包含 `.env`，可直接编辑）：

```bash
# 阿里云百炼 API 配置
OPENAI_API_KEY=sk-4603a51382c54499bcdf230be61420ab
OPENAI_MODEL=deepseek-v3.2
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 数据库配置
DB_PATH=chat_history.db

# HTTP 配置
HTTP_VERIFY_SSL=true
HTTP_TIMEOUT=60.0

# CORS 配置
CORS_ORIGINS=*
```

**必需的环境变量：**
- `OPENAI_API_KEY` - OpenAI API 密钥（必填）
- `OPENAI_MODEL` - 使用的模型（必填）
- `OPENAI_BASE_URL` - API 基础 URL（必填）
- `CORS_ORIGINS` - CORS 允许的源（必填）

### 3. 运行服务

```bash
# 使用脚本运行
./run.sh

# 或直接运行
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

服务将在 `http://localhost:8000` 启动。

### 4. 测试

```bash
# 健康检查
curl http://localhost:8000/health

# 聊天 API
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"你好"}]}'
```

---

## 📋 API 文档

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
  "model": "deepseek-v3.2"  // 可选，不提供则使用默认模型
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

**响应：**
```json
{
  "status": "healthy"
}
```

### GET /

根端点，返回API信息。

**响应：**
```json
{
  "message": "AI Chat API is running"
}
```

---

## 🚢 部署方案

### 方案 1：Render（推荐，完全免费）

**优点：**
- ✅ 完全免费
- ✅ 支持 Python/FastAPI/SQLite
- ✅ 代码无需改动
- ✅ 部署简单

**缺点：**
- ⚠️ 15 分钟无活动会休眠（首次访问需要 30-60 秒唤醒）

#### 部署步骤

1. **注册 Render**
   - 访问：https://render.com
   - 用 GitHub 登录

2. **创建 Web Service**
   - Dashboard → New → Web Service
   - 连接 GitHub 仓库
   - 选择包含 `chatback` 的仓库

3. **配置服务**
   - **Name**: `chatback`
   - **Region**: 选择离你近的（如 `Singapore`）
   - **Branch**: `main` 或 `master`
   - **Root Directory**: 留空（如果项目在根目录）或填写 `chatback`（如果在子目录）
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

4. **配置环境变量**
   在 Environment Variables 中添加：
   ```
   OPENAI_API_KEY=sk-4603a51382c54499bcdf230be61420ab
   OPENAI_MODEL=deepseek-v3.2
   OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
   DB_PATH=chat_history.db
   CORS_ORIGINS=*
   ```
   如果前端域名是 `debaosite.dpdns.org`，可以设置：
   ```
   CORS_ORIGINS=https://debaosite.dpdns.org,https://your-username.github.io
   ```

5. **部署**
   - 点击 "Create Web Service"
   - 等待部署完成（5-10 分钟）
   - 获取 URL：`https://your-app.onrender.com`

6. **测试**
   ```bash
   curl https://your-app.onrender.com/health
   ```

**注意：** Render 免费版会休眠，首次访问需要等待 30-60 秒唤醒。可以用免费监控服务（如 UptimeRobot）定期 ping 来保持活跃。

---

### 方案 2：Railway（$5/月免费额度）

**优点：**
- ✅ 不休眠，24/7 运行
- ✅ 稳定可靠
- ✅ 支持 Python/FastAPI/SQLite

**缺点：**
- ⚠️ 有 $5/月免费额度，超过需要付费（但小项目可能不超）

#### 部署步骤

1. **注册 Railway**
   - 访问：https://railway.app
   - 用 GitHub 登录

2. **创建项目**
   - New Project → Deploy from GitHub repo
   - 选择你的仓库

3. **配置环境变量**
   在项目设置中添加：
   ```
   OPENAI_API_KEY=sk-4603a51382c54499bcdf230be61420ab
   OPENAI_MODEL=deepseek-v3.2
   OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
   DB_PATH=chat_history.db
   CORS_ORIGINS=*
   ```

4. **获取部署地址**
   - Railway 会自动部署
   - 获取 URL：`https://your-app.railway.app`

---

### 方案 3：Replit（完全免费，无需信用卡）

**优点：**
- ✅ 完全免费
- ✅ 不需要信用卡
- ✅ 支持 Python/FastAPI/SQLite
- ✅ 有在线 IDE

**缺点：**
- ⚠️ 免费版需要保持浏览器标签页打开

#### 部署步骤

1. **注册 Replit**
   - 访问：https://replit.com
   - 用 GitHub 登录

2. **导入项目**
   - 点击 "Create Repl"
   - 选择 "Import from GitHub"
   - 输入：`https://github.com/de-bao/chatback`

3. **配置环境变量**
   - 点击左侧 "Secrets"（🔒图标）
   - 添加所有必需的环境变量

4. **安装依赖并运行**
   - 在终端运行：`pip install -r requirements.txt`
   - 创建 `main.py`：
     ```python
     import uvicorn
     from app import app
     
     if __name__ == "__main__":
         uvicorn.run(app, host="0.0.0.0", port=8080)
     ```
   - 点击 "Run" 按钮

5. **部署为 Web Service**
   - 点击左侧 "Deploy" 图标
   - 选择 "Deploy as Web Service"
   - 配置端口：`8080`

---

### 方案 4：PythonAnywhere（完全免费，无需信用卡）

**优点：**
- ✅ 完全免费
- ✅ 不需要信用卡
- ✅ 支持 Python/FastAPI/SQLite

**缺点：**
- ⚠️ 配置稍复杂
- ⚠️ 免费版限制较多

#### 部署步骤

1. **注册 PythonAnywhere**
   - 访问：https://www.pythonanywhere.com
   - 注册免费账户

2. **上传代码**
   - 在 Files 标签页上传项目文件
   - 或使用 Git 克隆：
     ```bash
     git clone https://github.com/de-bao/chatback.git
     ```

3. **安装依赖**
   - 在 Bash 控制台运行：
     ```bash
     pip3.10 install --user -r requirements.txt
     ```

4. **配置 Web App**
   - 在 Web 标签页创建新的 Web App
   - 选择 Flask（可以运行 FastAPI）
   - 配置 WSGI 文件指向你的 FastAPI 应用

5. **配置环境变量**
   - 在 Web App 设置中添加环境变量

---

## 🐛 故障排查

### 问题：服务启动失败

**检查：**
1. 所有必需的环境变量是否都配置了
2. 查看错误信息，确认缺少哪个环境变量
3. 检查 `.env` 文件是否存在且格式正确

### 问题：API 返回 500

**检查：**
1. 查看服务日志中的详细错误信息
2. 确认 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL` 是否正确
3. 测试 `/health` 端点是否正常
4. 检查数据库文件权限

### 问题：CORS 错误

**检查：**
1. 确认 `CORS_ORIGINS` 环境变量包含前端域名
2. 如果使用 `*`，确保没有其他 CORS 配置冲突

### 问题：数据库操作失败

**检查：**
1. 确认 `DB_PATH` 环境变量已设置
2. 检查数据库文件权限
3. 查看日志中的数据库错误信息

### 问题：Render 首次访问很慢

**原因：** 服务休眠了（免费版正常现象）

**解决：**
- 等待 30-60 秒，服务会自动唤醒
- 使用免费监控服务（如 UptimeRobot）定期 ping 保持活跃

---

## 📦 技术栈

- **FastAPI** - 现代 Python Web 框架
- **SQLite** - 轻量级文件数据库
- **SQLAlchemy** - Python ORM
- **OpenAI Python SDK** - OpenAI API 客户端
- **Uvicorn** - ASGI 服务器

---

## 📝 项目结构

```
chatback/
├── app.py              # FastAPI 应用主文件
├── models.py           # 数据库模型
├── database.py         # 数据库配置
├── requirements.txt    # Python 依赖
├── Procfile           # 部署配置（Railway/Render）
├── runtime.txt        # Python 版本
├── run.sh            # 启动脚本
├── worker.js         # Cloudflare Workers 路由脚本
├── wrangler.toml     # Cloudflare Workers 配置
├── package.json      # Node.js 依赖（用于 Workers）
├── .env              # 环境变量（已包含，可直接编辑）
└── README.md         # 本文档
```

---

---

## 🌐 通过 Cloudflare Workers 统一域名

如果你想让前端和后端使用同一个域名（如 `debaosite.dpdns.org`），可以使用 Cloudflare Workers 作为智能路由：

### 架构

```
debaosite.dpdns.org (用户访问的统一域名)
    ↓
Cloudflare Workers (智能路由)
    ├── /api/* → 后端 Replit 服务器 (https://chatback--debaocpc.replit.app)
    └── /* → GitHub Pages (前端)
```

### 部署步骤

#### 1. 安装 Wrangler CLI

```bash
npm install -g wrangler
```

#### 2. 登录 Cloudflare

```bash
wrangler login
```

#### 3. 配置环境变量

在 Cloudflare Dashboard 中配置：
1. 访问：https://dash.cloudflare.com
2. Workers & Pages → chat-api-router → Settings → Variables
3. 添加环境变量：
   - `BACKEND_URL` = `https://chatback--debaocpc.replit.app`
   - `FRONTEND_URL` = `https://your-username.github.io`（你的 GitHub Pages 地址）

#### 4. 部署 Workers

```bash
npm run deploy
```

或：

```bash
wrangler deploy
```

#### 5. 配置自定义域名

1. 在 Cloudflare Dashboard 中：
   - Workers & Pages → chat-api-router → Settings → Triggers
   - 添加 Custom Domain：`debaosite.dpdns.org`

2. 或者配置路由（在 `wrangler.toml` 中）：
   ```toml
   routes = [
     { pattern = "debaosite.dpdns.org/*", zone_name = "dpdns.org" }
   ]
   ```

### 最终效果

- 前端访问：`https://debaosite.dpdns.org/` → GitHub Pages
- API 访问：`https://debaosite.dpdns.org/api/chat` → Replit 后端
- API 访问：`https://debaosite.dpdns.org/api/chat/sessions` → Replit 后端

### 注意事项

- Workers 完全免费（每天 10 万次请求免费）
- 无需信用卡
- 自动处理 CORS
- 低延迟（边缘计算）

---

## 📄 许可证

MIT
