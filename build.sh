#!/bin/bash
# 完整的 Cloudflare Pages Flask 构建启动脚本

# ==============================
# 1. 基础配置（无需修改）
# ==============================
# Python 依赖安装目录（Cloudflare 无 root 权限，必须用用户目录）
PYTHON_USER_DIR=$(python3 -m site --user-base)
# 确保依赖目录加入环境变量（避免 "command not found: gunicorn"）
export PATH="$PYTHON_USER_DIR/bin:$PATH"

# ==============================
# 2. 安装项目依赖
# ==============================
echo "=== 开始安装依赖 ==="
# 升级 pip（避免旧版本安装失败）
python3 -m pip install --upgrade pip --user
# 安装 requirements.txt 中的所有依赖（Flask、gunicorn、requests）
python3 -m pip install -r requirements.txt --user

# 验证依赖安装（可选，用于调试，部署时可保留）
echo "=== 依赖安装验证 ==="
if ! command -v gunicorn &> /dev/null; then
    echo "❌ Gunicorn 安装失败，检查依赖配置！"
    exit 1
else
    echo "✅ Gunicorn 安装成功（版本：$(gunicorn --version | awk '{print $2}')）"
fi

if ! python3 -c "import requests" &> /dev/null; then
    echo "❌ Requests 安装失败，检查 requirements.txt！"
    exit 1
else
    echo "✅ Requests 安装成功"
fi

# ==============================
# 3. 启动 Flask 服务（核心步骤）
# ==============================
echo "=== 启动 Flask 服务 ==="
# 关键配置：
# - --bind 0.0.0.0:8080：Cloudflare 仅支持 8080 端口，必须绑定 0.0.0.0（允许外部访问）
# - app:app：对应你的 Flask 实例（app.py 文件 + app 实例名）
# - --workers 2：启动 2 个工作进程（适配 Cloudflare 资源限制，避免卡顿）
# - --timeout 60：延长超时时间（适配你的网络测试接口，避免上传文件时超时）
gunicorn \
  --bind 0.0.0.0:8080 \
  --workers 2 \
  --timeout 60 \
  --log-level=info \
  app:app

# ==============================
# 4. 异常处理（可选，增强稳定性）
# ==============================
if [ $? -ne 0 ]; then
    echo "❌ 服务启动失败！"
    exit 1
else
    echo "✅ 服务启动成功，监听 8080 端口"
fi