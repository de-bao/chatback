# 部署指南

## 架构说明

```
debaosite.dpdns.org (Cloudflare DNS)
    ↓
Cloudflare Workers (智能路由)
    ├── /api/* → 后端 FastAPI 服务器
    └── /* → GitHub Pages (前端)
```

## 部署步骤

### 方式一：通过 Cloudflare Dashboard 部署（推荐）

#### 1. 准备 GitHub 仓库

确保你的代码已经推送到 GitHub 仓库。

#### 2. 在 Cloudflare Dashboard 创建 Worker

1. 访问：https://dash.cloudflare.com → Workers & Pages → Create
2. 选择 **"Connect to Git"** 或 **"Import from GitHub"**
3. 授权 Cloudflare 访问你的 GitHub 仓库
4. 选择你的仓库（chatback 项目）

#### 3. 配置项目设置

在创建界面填写：

- **Project name**: `chat-api-router`
- **Build command**: 留空（Workers 不需要构建）
- **Deploy command**: `npx wrangler deploy`
- **Path**: `/`（项目根目录）
- **API token**: 会自动创建

#### 4. 配置环境变量

在项目设置中添加环境变量：

点击 **"Variables"** 或 **"Environment Variables"**，添加：

- **Variable name**: `BACKEND_URL`
- **Variable value**: `https://your-backend-server.com`（你的后端 FastAPI 地址）

- **Variable name**: `FRONTEND_URL`  
- **Variable value**: `https://your-username.github.io`（你的 GitHub Pages 地址）

#### 5. 配置自定义域名

1. 部署完成后，进入项目设置
2. 点击 **"Custom domains"** 或 **"Triggers"**
3. 添加自定义域名：`debaosite.dpdns.org`
4. Cloudflare 会自动配置 DNS

#### 6. 自动部署

- 每次推送到 GitHub 主分支，Cloudflare 会自动重新部署
- 可以在 Dashboard 查看部署历史和日志

---

### 方式二：手动部署（命令行）

如果你更喜欢命令行方式：

#### 1. 部署后端 FastAPI 服务器

后端需要部署到支持 Python 的服务器，推荐：

#### 选项 A：Railway（推荐，简单）
1. 注册 Railway：https://railway.app
2. 连接 GitHub 仓库
3. 部署后端项目
4. 获取部署后的 URL（如：`https://your-app.railway.app`）

#### 选项 B：Render
1. 注册 Render：https://render.com
2. 创建 Web Service
2. 连接 GitHub 仓库，选择 Python 环境
3. 获取部署后的 URL

#### 选项 C：Fly.io
1. 安装 flyctl：https://fly.io/docs/getting-started/
2. 运行 `fly launch`
3. 获取部署后的 URL

#### 选项 D：VPS 服务器
1. 在 VPS 上安装 Python、Nginx
2. 使用 systemd 或 supervisor 运行 FastAPI
3. 配置 Nginx 反向代理

### 2. 配置 Cloudflare Workers

#### 2.1 安装 Wrangler CLI

```bash
npm install -g wrangler
```

#### 2.2 登录 Cloudflare

```bash
wrangler login
```

#### 2.3 修改 worker.js

编辑 `worker.js`，替换以下变量：
- `BACKEND_URL`: 你的后端服务器地址
- `FRONTEND_URL`: 你的 GitHub Pages 地址

#### 2.4 部署 Workers

```bash
wrangler deploy
```

#### 2.5 配置自定义域名

1. 在 Cloudflare Dashboard 中
2. 进入 Workers & Pages
3. 选择你的 Worker
4. 添加自定义域名：`debaosite.dpdns.org`

### 3. 配置 DNS

在 Cloudflare DNS 中：
1. 确保 `debaosite.dpdns.org` 的 CNAME 指向 GitHub Pages
2. Workers 会自动拦截 `/api/*` 请求

或者：
1. 将 `debaosite.dpdns.org` 指向 Workers
2. Workers 路由 `/api/*` 到后端，其他到 GitHub Pages

### 4. 配置环境变量

在 Cloudflare Workers Dashboard 中配置：
- `BACKEND_URL`: 后端服务器地址
- `FRONTEND_URL`: GitHub Pages 地址

或者在 `wrangler.toml` 中配置（不推荐，敏感信息）

## 最终效果

- 前端访问：`debaosite.dpdns.org/` → GitHub Pages
- API 访问：`debaosite.dpdns.org/api/chat` → 后端 FastAPI
- API 访问：`debaosite.dpdns.org/api/chat/save` → 后端 FastAPI
- API 访问：`debaosite.dpdns.org/api/chat/sessions` → 后端 FastAPI

## 注意事项

1. **后端服务器**：需要 7x24 运行，确保可用性
2. **CORS**：后端代码中已配置 CORS，允许跨域
3. **环境变量**：后端的环境变量需要在部署平台配置
4. **数据库**：SQLite 文件需要持久化存储（考虑使用云存储或数据库）

## 优化建议

1. **使用 Cloudflare D1**：替代 SQLite，Cloudflare 原生数据库
2. **使用 KV 存储**：存储会话数据
3. **缓存策略**：在 Workers 中添加缓存层
