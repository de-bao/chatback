# Cloudflare Workers 部署步骤

## 部署架构

```
debaosite.dpdns.org (用户访问的统一域名)
    ↓
Cloudflare Workers (智能路由)
    ├── /api/* → 后端 FastAPI 服务器
    └── /* → GitHub Pages (前端)
```

## 第一步：部署后端 FastAPI 服务器

后端需要先部署到支持 Python 的服务器。推荐使用 **Railway**（最简单）：

### 使用 Railway 部署（推荐）

1. **注册 Railway**
   - 访问：https://railway.app
   - 使用 GitHub 账号登录

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择你的仓库（包含 `chatback` 项目的仓库）

3. **配置项目**
   - Railway 会自动检测到 Python 项目
   - 设置启动命令：`uvicorn app:app --host 0.0.0.0 --port $PORT`
   - Railway 会自动设置 `$PORT` 环境变量

4. **配置环境变量**
   在 Railway 项目设置中添加：
   ```
   OPENAI_API_KEY=sk-4603a51382c54499bcdf230be61420ab
   OPENAI_MODEL=deepseek-v3.2
   OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
   DB_PATH=chat_history.db
   CORS_ORIGINS=*
   ```

5. **获取部署地址**
   - 部署完成后，Railway 会提供一个 URL
   - 例如：`https://your-app.railway.app`
   - **记下这个地址，后面要用！**

### 其他部署选项

- **Render**: https://render.com（类似 Railway）
- **Fly.io**: https://fly.io（需要安装 flyctl）
- **VPS**: 自己搭建服务器

---

## 第二步：部署 Cloudflare Workers

### 方式一：通过 Cloudflare Dashboard（推荐）

1. **访问 Cloudflare Dashboard**
   - https://dash.cloudflare.com
   - 进入 **Workers & Pages** → **Create**

2. **连接 GitHub 仓库**
   - 选择 **"Connect to Git"** 或 **"Import from GitHub"**
   - 授权 Cloudflare 访问你的 GitHub
   - 选择包含 `chatback` 项目的仓库

3. **配置项目设置**
   - **Project name**: `chat-api-router`
   - **Build command**: 留空
   - **Deploy command**: `npx wrangler deploy`
   - **Path**: 
     - 如果 `chatback` 是仓库根目录 → `/`
     - 如果 `chatback` 在子目录 → `/chatback`
   - **API token**: 点击 "Create API token" 自动创建

4. **配置环境变量**
   部署完成后，在项目设置中添加：
   - 进入：**Workers & Pages** → **chat-api-router** → **Settings** → **Variables**
   - 添加环境变量：
     
     **BACKEND_URL**（必填）
     - Variable name: `BACKEND_URL`
     - Variable value: `https://your-app.railway.app`（第一步获取的后端地址）
     - 勾选：Production、Preview
     
     **FRONTEND_URL**（必填）
     - Variable name: `FRONTEND_URL`
     - Variable value: `https://your-username.github.io`（你的 GitHub Pages 地址）
     - 勾选：Production、Preview

5. **配置自定义域名**
   - 进入：**Workers & Pages** → **chat-api-router** → **Custom domains**
   - 点击 **Add Custom Domain**
   - 输入：`debaosite.dpdns.org`
   - Cloudflare 会自动配置 DNS

### 方式二：命令行部署

```bash
# 安装 Wrangler
npm install -g wrangler

# 登录 Cloudflare
wrangler login

# 配置环境变量
wrangler secret put BACKEND_URL
# 输入：https://your-app.railway.app

wrangler secret put FRONTEND_URL
# 输入：https://your-username.github.io

# 部署
wrangler deploy
```

---

## 第三步：验证部署

### 测试后端

```bash
# 测试后端健康检查
curl https://your-app.railway.app/health

# 测试后端聊天 API
curl -X POST https://your-app.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"你好"}]}'
```

### 测试 Workers 路由

```bash
# 测试前端（应该返回 GitHub Pages 页面）
curl https://debaosite.dpdns.org/

# 测试 API（应该转发到后端）
curl https://debaosite.dpdns.org/api/health

# 测试聊天 API
curl -X POST https://debaosite.dpdns.org/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"你好"}]}'
```

---

## 部署检查清单

- [ ] 后端 FastAPI 已部署到 Railway/Render 等
- [ ] 后端环境变量已配置（OPENAI_API_KEY 等）
- [ ] 后端可以正常访问（测试 /health 端点）
- [ ] Workers 项目已创建并连接 GitHub
- [ ] Workers 环境变量已配置（BACKEND_URL、FRONTEND_URL）
- [ ] 自定义域名已配置（debaosite.dpdns.org）
- [ ] 所有端点测试通过

---

## 常见问题

### 问题：Workers 部署失败

- 检查 `wrangler.toml` 中的 `name` 是否与 Project name 一致
- 检查 `worker.js` 文件是否存在
- 检查 Path 配置是否正确

### 问题：API 请求返回 500

- 检查 `BACKEND_URL` 环境变量是否正确
- 检查后端服务器是否正常运行
- 查看 Workers 日志：Dashboard → Logs

### 问题：前端页面无法访问

- 检查 `FRONTEND_URL` 环境变量是否正确
- 检查 GitHub Pages 是否正常部署
- 检查自定义域名 DNS 配置

---

## 下一步

部署完成后，前端就可以通过 `debaosite.dpdns.org/api/chat` 调用后端 API 了！
