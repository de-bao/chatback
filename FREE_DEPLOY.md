# 白嫖部署方案对比

## 你的需求
- ✅ 完全免费
- ✅ 运行 Python FastAPI + SQLite
- ✅ 长期可用

## 现实情况

**坏消息：** 没有完全免费且长期稳定的 Python 后端托管服务。

**好消息：** 有几个"几乎免费"的方案：

---

## 方案对比

### 方案 1：Render（推荐白嫖）

**免费额度：**
- ✅ 完全免费
- ✅ 支持 Python/FastAPI
- ✅ 支持 SQLite
- ⚠️ **15 分钟无活动会休眠**（首次访问需要几秒唤醒）
- ⚠️ 每月 750 小时免费（够用）

**适合：** 个人项目、低频访问

**部署步骤：**
1. 访问 https://render.com
2. 用 GitHub 登录
3. New → Web Service → 连接 GitHub 仓库
4. 配置：
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. 添加环境变量（同 Railway）

---

### 方案 2：Railway（$5/月免费额度）

**免费额度：**
- ✅ $5/月免费额度
- ✅ 不休眠，24/7 运行
- ✅ 支持 Python/FastAPI/SQLite
- ⚠️ 超过 $5 要付费（但小项目可能不超）

**适合：** 需要 24/7 运行的项目

**成本估算：**
- 小项目（低流量）：可能不花钱
- 中等项目：$5-10/月
- 大项目：需要付费

---

### 方案 3：Fly.io（免费额度）

**免费额度：**
- ✅ 3 个共享 CPU 实例免费
- ✅ 3GB 持久化存储免费
- ✅ 支持 Python/FastAPI
- ⚠️ 需要信用卡验证（但不扣钱，除非超限）

**适合：** 需要持久化存储的项目

---

### 方案 4：完全用 Cloudflare Workers（需重写代码）

**免费额度：**
- ✅ 完全免费
- ✅ 每天 10 万次请求
- ✅ 无休眠问题
- ❌ **需要重写代码**：
  - 用 JavaScript/TypeScript 重写
  - 用 Workers KV 替代 SQLite
  - 失去 SQLAlchemy ORM

**适合：** 愿意重写代码的项目

---

## 推荐方案

### 如果不想改代码：**Render（方案 1）**

**优点：**
- 完全免费
- 代码无需改动
- 部署简单

**缺点：**
- 15 分钟无活动会休眠（首次访问慢几秒）

### 如果需要 24/7 运行：**Railway（方案 2）**

**优点：**
- 不休眠
- 稳定

**缺点：**
- 可能产生费用（但小项目可能不超免费额度）

---

## 部署到 Render（完全免费）

### 步骤 1：准备项目

确保项目有：
- ✅ `requirements.txt`
- ✅ `Procfile`（已创建）
- ✅ `.env` 文件（环境变量）

### 步骤 2：部署到 Render

1. **注册 Render**
   - https://render.com
   - 用 GitHub 登录

2. **创建 Web Service**
   - Dashboard → New → Web Service
   - 连接 GitHub 仓库
   - 选择包含 `chatback` 的仓库

3. **配置服务**
   - **Name**: `chatback`（随便起）
   - **Region**: 选离你近的（如 Singapore）
   - **Branch**: `main` 或 `master`
   - **Root Directory**: `/chatback`（如果项目在子目录）
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

5. **部署**
   - 点击 "Create Web Service"
   - 等待部署完成（5-10 分钟）
   - 获取 URL：`https://your-app.onrender.com`

### 步骤 3：测试

```bash
# 测试健康检查
curl https://your-app.onrender.com/health

# 测试聊天 API
curl -X POST https://your-app.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"你好"}]}'
```

---

## 注意事项

### Render 休眠问题

- **问题**：15 分钟无活动会休眠
- **影响**：首次访问需要 30-60 秒唤醒
- **解决**：
  1. 用免费监控服务定期 ping（如 UptimeRobot）
  2. 或者接受首次访问慢一点
  3. 或者升级到付费版（$7/月，不休眠）

### SQLite 持久化

- Render 的免费层**会持久化文件**
- SQLite 数据库文件会保留
- 但服务重启后数据还在

---

## 总结

**最推荐：Render（完全免费，代码不改）**

如果接受首次访问慢几秒，Render 是最佳白嫖方案！
