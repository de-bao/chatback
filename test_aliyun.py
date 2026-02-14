#!/usr/bin/env python3
"""
测试阿里云百炼 DeepSeek v3.2 API 连接
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
import httpx

# 加载环境变量
load_dotenv()

# 读取配置
api_key = os.getenv('OPENAI_API_KEY')
base_url = os.getenv('OPENAI_BASE_URL')
model = os.getenv('OPENAI_MODEL')
verify_ssl = os.getenv('HTTP_VERIFY_SSL', 'true').lower() == 'true'
timeout = float(os.getenv('HTTP_TIMEOUT', '60.0'))

print("=" * 50)
print("测试阿里云百炼 DeepSeek v3.2 API 连接")
print("=" * 50)
print(f"API Key: {api_key[:20]}..." if api_key else "API Key: 未设置")
print(f"Base URL: {base_url}")
print(f"Model: {model}")
print(f"Verify SSL: {verify_ssl}")
print(f"Timeout: {timeout}s")
print("=" * 50)

if not api_key or not base_url or not model:
    print("❌ 配置不完整，请检查 .env 文件")
    exit(1)

# 创建 HTTP 客户端
transport = httpx.HTTPTransport(proxy=None, verify=verify_ssl)
http_client = httpx.Client(transport=transport, timeout=timeout)

# 创建 OpenAI 客户端
client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    http_client=http_client
)

try:
    print("\n1. 测试非流式请求...")
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'user', 'content': '你好，请简单介绍一下你自己，用一句话即可'}
        ],
        max_tokens=100
    )
    
    print("✅ 非流式请求成功！")
    print(f"模型: {completion.model}")
    print(f"回复: {completion.choices[0].message.content}\n")
    
    print("2. 测试流式请求（带深度思考）...")
    messages = [{"role": "user", "content": "你是谁"}]
    stream = client.chat.completions.create(
        model="deepseek-v3.2",
        messages=messages,
        extra_body={"enable_thinking": True},
        stream=True,
        max_tokens=100
    )
    
    is_answering = False
    thinking_content = ""
    answer_content = ""
    
    print("接收流式响应...")
    for chunk in stream:
        delta = chunk.choices[0].delta
        if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
            if not is_answering:
                thinking_content += delta.reasoning_content
        if hasattr(delta, "content") and delta.content:
            if not is_answering:
                is_answering = True
            answer_content += delta.content
    
    if thinking_content:
        print(f"\n思考过程: {thinking_content[:200]}..." if len(thinking_content) > 200 else f"\n思考过程: {thinking_content}")
    if answer_content:
        print(f"回复: {answer_content}")
    
    print("\n✅ 流式请求（深度思考）成功！")
    print("\n✅ DeepSeek v3.2 API 配置正确，可以正常使用！")
    
except Exception as e:
    print(f"\n❌ 连接失败: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
