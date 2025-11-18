#!/bin/bash
# 适配 network-tester.py 的 Cloudflare Pages 构建启动脚本

# ==============================
# 1. 基础配置（无需修改）
# ==============================
PYTHON_USER_DIR=$(python3 -m site --user-base)
export PATH="$PYTHON_USER_DIR/bin:$PATH"

# ==============================
# 2. 安装项目依赖
# ==============================
echo "=== 开始安装依赖 ==="
python3 -m pip install --upgrade pip --user
python3 -m pip install -r requirements.txt --user

# 验证依赖安装
echo "=== 依赖安装验证 ==="
if ! python3 -c "import gunicorn" &> /dev/null; then
    echo "❌ Gunicorn 安装失败，检查 requirements.txt！"
    exit 1
else
    echo "✅ Gunicorn 安装成功"
fi

if ! python3 -c "import requests" &> /dev/null; then
    echo "❌ Requests 安装失败，检查 requirements.txt！"
    exit 1
else
    echo "✅ Requests 安装成功"
fi

# ==============================
# 3. 启动 Flask 服务（核心修改：模块名改为 network-tester）
# ==============================
echo "=== 启动 Flask 服务 ==="
# 关键：network-tester 是文件名（不含 .py），app 是 Flask 实例名（你的代码中是 app = Flask(__name__)）
python3 -m gunicorn \
  --bind 0.0.0.0:8080 \
  --workers 2 \
  --timeout 60 \
  --log-level=info \
  network-tester:app

# ==============================
# 4. 异常处理
# ==============================
if [ $? -ne 0 ]; then
    echo "❌ 服务启动失败！"
    exit 1
else
    echo "✅ 服务启动成功，监听 8080 端口"
fi