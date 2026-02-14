# Render 部署指南（完全免费）

## 前置准备

✅ 项目已准备好：
- `requirements.txt` ✓
- `Procfile` ✓
- `app.py` 已配置环境变量 ✓

## 部署步骤

### 第一步：注册 Render

1. 访问：https://render.com
2. 点击 **"Get Started for Free"**
3. 选择 **"Sign up with GitHub"**（推荐，方便连接仓库）

### 第二步：创建 Web Service

1. 登录后，点击 Dashboard 右上角的 **"New +"**
2. 选择 **"Web Service"**
3. 点击 **"Connect account"** 连接你的 GitHub
4. 选择包含 `chatback` 项目的仓库
5. 点击 **"Connect"**

### 第三步：配置服务

在配置页面填写：

#### 基本信息
- **Name**: `chatback`（或你喜欢的名字）
- **Region**: 选择离你近的（如 `Singapore` 或 `Oregon (US West)`）
- **Branch**: `main` 或 `master`（根据你的仓库）
- **Root Directory**: 
  - 如果 `chatback` 是仓库根目录 → 留空
  - 如果 `chatback` 在子目录 → 填写 `chatback`

#### 构建和启动
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

#### 环境变量（重要！）

点击 **"Advanced"** → **"Add Environment Variable"**，添加以下变量：

```
OPENAI_API_KEY=sk-4603a51382c54499bcdf230be61420ab
OPENAI_MODEL=deepseek-v3.2
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
DB_PATH=chat_history.db
CORS_ORIGINS=*
```

**注意：** 如果前端域名是 `debaosite.dpdns.org`，可以设置：
```
CORS_ORIGINS=https://debaosite.dpdns.org,https://your-username.github.io
```

### 第四步：部署

1. 滚动到底部，点击 **"Create Web Service"**
2. 等待部署完成（5-10 分钟）
3. 部署完成后，你会看到服务 URL，例如：`https://chatback-xxxx.onrender.com`

### 第五步：测试

部署完成后，测试 API：

```bash
# 测试健康检查
curl https://your-app.onrender.com/health

# 测试聊天 API
curl -X POST https://your-app.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"你好"}]}'
```

---

## 配置前端

在你的前端项目中，修改 API 地址：

```javascript
// 把 API 地址改成 Render 的地址
const API_BASE_URL = 'https://your-app.onrender.com';
```

---

## 注意事项

### 1. 休眠问题

- **问题**：Render 免费版在 15 分钟无活动后会休眠
- **影响**：首次访问需要 30-60 秒唤醒
- **解决**：
  - 接受首次访问慢一点（免费嘛）
  - 或者用免费监控服务定期 ping（如 UptimeRobot）

### 2. 数据库持久化

- ✅ SQLite 数据库文件会持久化保存
- ✅ 服务重启后数据不会丢失
- ✅ 可以正常使用

### 3. 日志查看

- 在 Render Dashboard 中点击你的服务
- 点击 **"Logs"** 标签查看实时日志
- 可以调试问题

### 4. 自动部署

- ✅ 每次推送到 GitHub 主分支，Render 会自动重新部署
- ✅ 可以在 **"Events"** 标签查看部署历史

---

## 故障排查

### 问题：部署失败

**检查：**
1. `requirements.txt` 是否存在
2. `Procfile` 是否存在
3. 环境变量是否都配置了
4. 查看 **Logs** 标签的错误信息

### 问题：API 返回 500

**检查：**
1. 查看 **Logs** 标签的错误信息
2. 确认所有环境变量都配置了
3. 测试 `/health` 端点是否正常

### 问题：首次访问很慢

**原因：** 服务休眠了（免费版正常现象）

**解决：** 等待 30-60 秒，服务会自动唤醒

---

## 升级到付费版（可选）

如果不想休眠，可以升级到 **Starter** 计划：
- 价格：$7/月
- 不休眠
- 更快的启动速度

但对于个人项目，免费版够用了！

---

## 完成！

部署完成后，你的后端就可以通过 Render 的 URL 访问了！

**下一步：** 修改前端代码，把 API 地址改成 Render 的地址。
