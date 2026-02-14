# 快速部署指南（Cloudflare Dashboard）

## 通过 Cloudflare Dashboard 部署 Workers

### 步骤 1：准备 GitHub 仓库

确保你的 `chatback` 项目已经推送到 GitHub。

### 步骤 2：在 Cloudflare Dashboard 创建 Worker

1. 访问：https://dash.cloudflare.com → **Workers & Pages** → **Create**
2. 选择 **"Connect to Git"** 或点击 **"Import from GitHub"**
3. 授权 Cloudflare 访问你的 GitHub 账户
4. 选择你的仓库（包含 `chatback` 项目的仓库）

### 步骤 3：配置项目设置

在创建界面填写：

- **Project name**: `chat-api-router`
- **Build command**: 留空（Workers 不需要构建）
- **Deploy command**: `npx wrangler deploy`
- **Path**: `/chatback`（如果你的项目在子目录）或 `/`（如果在根目录）
- **API token**: 会自动创建，点击 "Create API token"

### 步骤 4：配置环境变量

部署完成后，在项目设置中添加环境变量：

1. 进入项目：**Workers & Pages** → **chat-api-router**
2. 点击 **Settings** → **Variables**
3. 在 **Environment Variables** 中添加：

   **变量 1：**
   - Variable name: `BACKEND_URL`
   - Variable value: `https://your-backend-server.com`（你的后端 FastAPI 地址）
   - 勾选所有环境（Production、Preview）

   **变量 2：**
   - Variable name: `FRONTEND_URL`
   - Variable value: `https://your-username.github.io`（你的 GitHub Pages 地址）
   - 勾选所有环境（Production、Preview）

### 步骤 5：配置自定义域名

1. 在项目页面，点击 **Custom domains** 或 **Triggers**
2. 点击 **Add Custom Domain**
3. 输入：`debaosite.dpdns.org`
4. Cloudflare 会自动配置 DNS 记录

### 步骤 6：验证部署

部署完成后，测试：

- 前端：访问 `https://debaosite.dpdns.org/` 应该看到你的前端页面
- API：访问 `https://debaosite.dpdns.org/api/health` 应该返回 `{"status":"healthy"}`

## 自动部署

- 每次推送到 GitHub 主分支，Cloudflare 会自动重新部署
- 可以在 Dashboard 的 **Deployments** 标签查看部署历史
- 可以在 **Logs** 标签查看实时日志

## 注意事项

1. **后端服务器必须先部署**：确保你的 FastAPI 后端已经部署并运行
2. **环境变量必须配置**：`BACKEND_URL` 和 `FRONTEND_URL` 必须正确配置
3. **路径配置**：如果项目在 GitHub 仓库的子目录，Path 要填写正确
4. **DNS 配置**：如果自定义域名不生效，检查 Cloudflare DNS 设置

## 故障排查

### 问题：部署失败

- 检查 `wrangler.toml` 中的 `name` 是否与 Project name 一致
- 检查 `worker.js` 文件是否存在
- 查看部署日志中的错误信息

### 问题：API 请求失败

- 检查 `BACKEND_URL` 环境变量是否正确
- 检查后端服务器是否正常运行
- 查看 Workers 日志

### 问题：前端页面无法访问

- 检查 `FRONTEND_URL` 环境变量是否正确
- 检查 GitHub Pages 是否正常部署
- 检查自定义域名 DNS 配置
