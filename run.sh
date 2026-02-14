#!/bin/bash

# 启动AI聊天后端服务
# 使用虚拟环境
source /home/10355407/baode311env/bin/activate
uvicorn app:app --reload --host 0.0.0.0 --port 8000
