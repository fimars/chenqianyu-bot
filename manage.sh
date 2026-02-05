#!/bin/bash
# 陈千语 Bot 管理脚本喵～

SERVICE_NAME="com.chenqianyu.bot"
PLIST_PATH="$HOME/Library/LaunchAgents/$SERVICE_NAME.plist"
BOT_DIR="$HOME/workspace/chenqianyu-bot"

show_help() {
    echo "🐼 陈千语 Bot 管理脚本"
    echo ""
    echo "用法: ./manage.sh [命令]"
    echo ""
    echo "命令:"
    echo "  start    - 启动 Bot"
    echo "  stop     - 停止 Bot"
    echo "  restart  - 重启 Bot"
    echo "  status   - 查看状态"
    echo "  logs     - 查看日志"
    echo "  install  - 安装开机启动服务"
    echo "  uninstall - 卸载开机启动服务"
    echo "  help     - 显示帮助"
}

start_bot() {
    echo "🚀 启动陈千语 Bot..."
    if launchctl list | grep -q "$SERVICE_NAME"; then
        echo "⚠️  Bot 已经在运行了喵～"
    else
        launchctl load "$PLIST_PATH" 2>/dev/null
        sleep 2
        if launchctl list | grep -q "$SERVICE_NAME"; then
            echo "✅ Bot 启动成功！端口: 3993 喵～"
        else
            echo "❌ Bot 启动失败，请检查日志喵～"
        fi
    fi
}

stop_bot() {
    echo "🛑 停止陈千语 Bot..."
    if launchctl list | grep -q "$SERVICE_NAME"; then
        launchctl unload "$PLIST_PATH" 2>/dev/null
        echo "✅ Bot 已停止喵～"
    else
        echo "⚠️  Bot 没有在运行喵～"
    fi
}

restart_bot() {
    echo "🔄 重启陈千语 Bot..."
    stop_bot
    sleep 1
    start_bot
}

check_status() {
    echo "📊 陈千语 Bot 状态:"
    echo ""
    if launchctl list | grep -q "$SERVICE_NAME"; then
        echo "✅ 状态: 运行中"
        PID=$(launchctl list | grep "$SERVICE_NAME" | awk '{print $1}')
        echo "📝 PID: $PID"
    else
        echo "❌ 状态: 未运行"
    fi
    echo "🔌 端口: 3993"
    echo "📁 目录: $BOT_DIR"
    echo "📝 日志: $BOT_DIR/logs/"
}

show_logs() {
    echo "📝 查看日志 (按 Ctrl+C 退出)..."
    if [ -f "$BOT_DIR/logs/bot.out.log" ]; then
        tail -f "$BOT_DIR/logs/bot.out.log"
    else
        echo "暂无日志文件喵～"
    fi
}

install_service() {
    echo "📦 安装开机启动服务..."
    if [ -f "$PLIST_PATH" ]; then
        echo "✅ 服务文件已存在"
    else
        echo "❌ 服务文件不存在，请检查配置喵～"
        exit 1
    fi
    
    # 确保目录存在
    mkdir -p "$BOT_DIR/logs"
    
    # 如果正在运行，先停止
    if launchctl list | grep -q "$SERVICE_NAME"; then
        launchctl unload "$PLIST_PATH" 2>/dev/null
    fi
    
    # 加载服务
    launchctl load "$PLIST_PATH"
    
    echo "✅ 开机启动服务已安装并启动！"
    echo "   服务名: $SERVICE_NAME"
    echo "   端口: 3993"
}

uninstall_service() {
    echo "🗑️  卸载开机启动服务..."
    if launchctl list | grep -q "$SERVICE_NAME"; then
        launchctl unload "$PLIST_PATH" 2>/dev/null
        echo "✅ 服务已卸载喵～"
    else
        echo "⚠️  服务未运行喵～"
    fi
}

# 主程序
case "$1" in
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        restart_bot
        ;;
    status)
        check_status
        ;;
    logs)
        show_logs
        ;;
    install)
        install_service
        ;;
    uninstall)
        uninstall_service
        ;;
    help|*)
        show_help
        ;;
esac
