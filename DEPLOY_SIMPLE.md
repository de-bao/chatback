# 简化部署方案（不用 Workers，推荐！）

## 方案：直接部署 FastAPI，前端直接调用

既然 Workers 只是转发，那**干脆不用 Workers**，直接部署后端，前端直接调用！

### 架构

```
前端 (GitHub Pages: debaosite.dpdns.org)
    ↓ 直接调用（配置 CORS）
后端 FastAPI (Railway/Render: https://your-backend.railway.app)
```

**优势：**
- ✅ 只需部署一个服务（后端）
- ✅ 少一层转发，延迟更低
- ✅ 配置简单，维护方便
- ✅ 不需要 Workers 配置

### 部署步骤

#### 第一步：部署 FastAPI 后端到 Railway

1. **访问 Railway**
   - https://railway.app
   - 用 GitHub 登录

2. **创建项目**
   - New Project → Deploy from GitHub repo
   - 选择你的仓库

3. **配置环境变量**
   ```
   OPENAI_API_KEY=sk-4603a51382c54499bcdf230be61420ab
   OPENAI_MODEL=deepseek-v3.2
   OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
   DB_PATH=chat_history.db
   CORS_ORIGINS=https://debaosite.dpdns.org,https://your-username.github.io
   ```
   **注意**：`CORS_ORIGINS` 要包含你的前端域名！

4. **获取后端地址**
   - Railway 会给你一个 URL，例如：`https://chatback-production.up.railway.app`
   - **记下这个地址！**

#### 第二步：修改前端配置

在你的前端项目中，修改 API 调用地址：

```javascript
// 前端代码中，把 API 地址改成后端地址
const API_BASE_URL = 'https://your-backend.railway.app';
```

#### 第三步：配置自定义域名（可选）

如果你想用 `api.debaosite.dpdns.org` 作为后端地址：

1. 在 Railway 项目设置中添加自定义域名
2. 配置 DNS：`api.debaosite.dpdns.org` → CNAME → Railway 提供的地址
3. 前端调用：`https://api.debaosite.dpdns.org/api/chat`

---

## 对比：用 Workers vs 不用 Workers

| 方案 | 优点 | 缺点 |
|------|------|------|
| **不用 Workers（推荐）** | ✅ 简单，只需部署一个后端<br>✅ 少一层转发，延迟更低<br>✅ 不需要配置 Workers | ❌ 前端和后端域名不同（可以接受） |
| **用 Workers** | ✅ 统一域名<br>✅ 可以做边缘缓存 | ❌ 需要部署两个服务<br>❌ 多一层转发<br>❌ 配置更复杂 |

---

## 推荐：不用 Workers

**理由：**
1. 你的应用不需要 Workers 的边缘计算能力
2. 多一层转发只会增加延迟
3. 部署和维护更简单

**如果一定要统一域名**，可以：
- 后端用子域名：`api.debaosite.dpdns.org`
- 前端用主域名：`debaosite.dpdns.org`

这样也很清晰！

---

## 测试

部署完成后测试：

```bash
# 测试后端
curl https://your-backend.railway.app/health

# 测试聊天 API
curl -X POST https://your-backend.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"你好"}]}'
```
