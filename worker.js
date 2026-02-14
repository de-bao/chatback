/**
 * Cloudflare Workers 智能路由
 * - /api/* -> 转发到后端 Replit 服务器
 * - /health -> 转发到后端 Replit 服务器
 * - 其他路径 -> 转发到 Replit 前端 /docs
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // 从环境变量读取配置
    const BACKEND_URL = env.BACKEND_URL || 'https://chatback--debaocpc.replit.app';
    const FRONTEND_URL = env.FRONTEND_URL || 'https://chatback--debaocpc.replit.app/docs';

    // 处理 OPTIONS 预检请求
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization',
          'Access-Control-Max-Age': '86400',
        },
      });
    }

    // 处理 API 请求 - 转发到后端
    // 包括 /api/* 路径和 /health 路径
    if (path.startsWith('/api/') || path === '/health') {
      return handleApiRequest(request, BACKEND_URL);
    }

    // 处理前端请求 - 转发到 Replit 前端
    return handleFrontendRequest(request, FRONTEND_URL);
  }
};

/**
 * 处理 API 请求，转发到后端服务器
 */
async function handleApiRequest(request, backendUrl) {
  try {
    // 构建后端 URL
    const url = new URL(request.url);
    const backendRequestUrl = `${backendUrl}${url.pathname}${url.search}`;

    // 创建新的请求，转发所有头部和 body
    // 移除 Host 头，避免后端服务器混淆
    const headers = new Headers(request.headers);
    headers.delete('Host');
    headers.set('X-Forwarded-Host', url.host);
    headers.set('X-Forwarded-Proto', url.protocol.slice(0, -1));

    const backendRequest = new Request(backendRequestUrl, {
      method: request.method,
      headers: headers,
      body: request.body,
    });

    // 转发请求到后端
    const response = await fetch(backendRequest);

    // 创建响应，添加 CORS 头
    const newHeaders = new Headers(response.headers);
    newHeaders.set('Access-Control-Allow-Origin', '*');
    newHeaders.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    newHeaders.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    newHeaders.set('Access-Control-Allow-Credentials', 'true');

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: newHeaders,
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
    });
  }
}

/**
 * 处理前端请求，转发到 Replit 前端
 */
async function handleFrontendRequest(request, frontendUrl) {
  try {
    const url = new URL(request.url);
    // 前端 URL 指向 Replit 的 /docs 路径
    // 如果访问根路径，转发到 frontendUrl（已包含 /docs），否则拼接路径
    let frontendRequestUrl;
    if (url.pathname === '/' || url.pathname === '') {
      // 根路径，直接使用 frontendUrl（已包含 /docs）
      frontendRequestUrl = frontendUrl.endsWith('/') ? frontendUrl.slice(0, -1) : frontendUrl;
    } else {
      // 其他路径，拼接（注意：如果 frontendUrl 是 /docs，则路径会是 /docs/xxx）
      frontendRequestUrl = `${frontendUrl}${url.pathname}${url.search}`;
    }

    const frontendRequest = new Request(frontendRequestUrl, {
      method: request.method,
      headers: request.headers,
    });

    const response = await fetch(frontendRequest);

    // 返回 Replit 前端的响应
    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
