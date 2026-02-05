#!/bin/bash
# 启动脚本喵～

echo "🐼 启动陈千语的 Telegram Bot..."

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python3"
    exit 1
fi

# 检查虚拟环境
if [ -d "venv" ]; then
    echo "✅ 激活虚拟环境..."
    source venv/bin/activate
fi

# 检查依赖
echo "📦 检查依赖..."
pip install -q -r requirements.txt

# 运行 Bot
echo "🚀 启动 Bot..."
python3 bot.py
