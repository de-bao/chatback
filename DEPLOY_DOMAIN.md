# 域名配置方案

## 当前情况

- 前端：`https://chatback--debaocpc.replit.app/docs`（Replit）
- 后端 API：`https://chatback--debaocpc.replit.app`
- Workers：`https://chat-api-router.debao-cpc.workers.dev`

## 方案 1：使用子域名（推荐）

### 配置步骤

1. **在 Cloudflare DNS 中添加子域名**
   - 类型：`CNAME`
   - 名称：`api`
   - 内容：`chat-api-router.debao-cpc.workers.dev`
   - 代理状态：**Proxied**（橙色云朵）

2. **在 Cloudflare Workers 中添加自定义域名**
   - Workers & Pages → chat-api-router → Settings → Triggers
   - Add Custom Domain
   - 输入：`api.debaosite.dpdns.org`

3. **前端调用 API**
   ```javascript
   // 前端代码中
   const API_BASE_URL = 'https://api.debaosite.dpdns.org';
   ```

### 最终效果

- 前端：`https://api.debaosite.dpdns.org/` → Workers → Replit `/docs`
- API：`https://api.debaosite.dpdns.org/api/chat` → Workers → Replit 后端

---

## 方案 2：统一域名（需要修改 DNS）

### 配置步骤

1. **修改 DNS 记录**
   - 将 `debaosite.dpdns.org` 的 CNAME 改为指向 Workers
   - 或者删除现有 CNAME，让 Workers 处理

2. **在 Cloudflare Workers 中添加自定义域名**
   - Workers & Pages → chat-api-router → Settings → Triggers
   - Add Custom Domain
   - 输入：`debaosite.dpdns.org`

3. **确保 Workers 路由正确**
   - `/api/*` → 后端
   - `/health` → 后端
   - `/*` → Replit `/docs`

### 最终效果

- 前端：`https://debaosite.dpdns.org/` → Workers → Replit `/docs`
- API：`https://debaosite.dpdns.org/api/chat` → Workers → Replit 后端

---

## 推荐：方案 1（子域名）

**优点：**
- ✅ 前后端分离更清晰
- ✅ 配置简单
- ✅ 统一使用 Replit 服务

**缺点：**
- ⚠️ 需要前端代码修改 API 地址为 `api.debaosite.dpdns.org`
