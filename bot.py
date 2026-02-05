#!/usr/bin/env python3
"""
陈千语的 Telegram Bot - 通过 Opencode CLI 提供 AI 回复喵～

使用方法:
    python bot.py

环境变量:
    TELEGRAM_BOT_TOKEN - Telegram Bot Token
    OPENCODE_CLI - Opencode CLI 路径（默认: opencode）
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
from telegram import Update, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from message_handler import MessageHandler as OpencodeHandler, SimpleMessageHandler


# 配置日志格式
class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""

    COLORS = {
        "DEBUG": "\033[36m",  # 青色
        "INFO": "\033[32m",  # 绿色
        "WARNING": "\033[33m",  # 黄色
        "ERROR": "\033[31m",  # 红色
        "CRITICAL": "\033[35m",  # 紫色
    }
    RESET = "\033[0m"

    def format(self, record):
        # 简化 logger 名称
        if record.name.startswith("telegram"):
            record.name = "TG"
        elif record.name.startswith("httpx"):
            record.name = "HTTP"
        elif len(record.name) > 15:
            record.name = record.name[:12] + "..."

        # 添加颜色
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"

        # 格式化时间
        record.asctime = self.formatTime(record, "%H:%M:%S")

        return super().format(record)


# 创建处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, Config.LOG_LEVEL))

# 设置格式
formatter = ColoredFormatter(
    fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s", datefmt="%H:%M:%S"
)
console_handler.setFormatter(formatter)

# 配置根日志器
root_logger = logging.getLogger()
root_logger.setLevel(getattr(logging, Config.LOG_LEVEL))
root_logger.handlers = []  # 清除默认处理器
root_logger.addHandler(console_handler)

# 抑制第三方库的冗余日志
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.INFO)

logger = logging.getLogger(__name__)

# 初始化消息处理器
try:
    handler = OpencodeHandler()
    logger.info("使用 Opencode CLI 消息处理器")
except Exception as e:
    logger.warning(f"Opencode 处理器初始化失败，使用简化版: {e}")
    handler = SimpleMessageHandler()


def check_user_permission(user_id: int) -> bool:
    """检查用户是否有权限访问"""
    if not Config.ALLOWED_USER_ID:
        return True  # 如果没有设置白名单，允许所有用户
    allowed_ids = [int(uid.strip()) for uid in Config.ALLOWED_USER_ID.split(",")]
    return user_id in allowed_ids


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """发送欢迎消息"""
    user = update.effective_user

    # 检查用户权限
    if not check_user_permission(user.id):
        await update.message.reply_text("抱歉，你没有权限使用这个 Bot 喵～🐼")
        logger.warning(f"未授权用户尝试访问: {user.id} ({user.username})")
        return

    welcome_msg = f"""你好 {user.first_name}！我是陈千语喵～🐼

我是通过 Opencode AI 驱动的 Telegram Bot！
你可以直接给我发消息，我会让 AI 助手来回复你喵～

可用命令：
/start - 开始聊天
/help - 显示帮助
/ping - 检查状态

发送任何消息都会触发 AI 回复喵～"""

    await update.message.reply_text(welcome_msg)
    logger.info(f"用户 {user.id} ({user.username}) 启动了 bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """发送帮助信息"""
    user = update.effective_user

    # 检查用户权限
    if not check_user_permission(user.id):
        return

    help_text = """📖 帮助信息喵～

🤖 关于我：
我是陈千语，来自明日方舟世界观的角色，由 Opencode AI 驱动喵～

💬 使用方法：
直接发送消息给我，我会调用 AI 来回复你！

⌨️ 可用命令：
/start - 开始聊天
/help - 显示帮助  
/ping - 检查 bot 状态

📝 提示：
- 我会保持角色设定说话
- 每句话结尾都会有"喵"
- 如果有问题请联系管理员

🐼 祝你使用愉快喵～"""

    await update.message.reply_text(help_text)


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ping 命令"""
    user = update.effective_user

    # 检查用户权限
    if not check_user_permission(user.id):
        return

    await update.message.reply_text("✅ Pong! Bot 运行正常喵～🐼")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理收到的消息"""
    user = update.effective_user
    message_text = update.message.text

    # 检查用户权限
    if not check_user_permission(user.id):
        await update.message.reply_text("抱歉，你没有权限使用这个 Bot 喵～🐼")
        logger.warning(f"未授权用户尝试发消息: {user.id} ({user.username})")
        return

    logger.info(f"收到来自 {user.id} ({user.username}) 的消息: {message_text}")

    # 显示"正在输入..."状态
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        # 调用消息处理器获取回复
        response = handler.process_message(
            user_id=user.id,
            username=user.username or user.first_name,
            message_text=message_text,
        )

        # 检测图片标记 [IMAGE:路径]
        import re
        image_pattern = r'\[IMAGE:([^\]]+)\]'
        image_match = re.search(image_pattern, response)
        image_path = None

        if image_match:
            image_path = image_match.group(1).strip()
            # 从回复中移除图片标记
            response = re.sub(image_pattern, '', response).strip()

        # 按 3 个换行符分割消息，分多次发送
        messages = [msg.strip() for msg in response.split("\n\n\n") if msg.strip()]

        if not messages:
            messages = [response]

        for i, msg in enumerate(messages):
            if msg:  # 只发送非空消息
                await update.message.reply_text(msg)
                logger.info(f"已发送第 {i + 1}/{len(messages)} 条消息给用户 {user.id}")

                # 多条消息之间间隔 600ms
                if i < len(messages) - 1:
                    await asyncio.sleep(0.6)

        # 如果有图片，发送图片
        if image_path and os.path.exists(image_path):
            try:
                with open(image_path, 'rb') as photo:
                    await update.message.reply_photo(photo=InputFile(photo))
                logger.info(f"已发送图片给用户 {user.id}: {image_path}")
            except Exception as img_err:
                logger.error(f"发送图片失败: {img_err}")
                await update.message.reply_text(f"图片生成好了，但发送失败了喵～({img_err})")

    except Exception as e:
        logger.error(f"处理消息时出错: {e}")
        await update.message.reply_text("抱歉，处理消息时出错了喵～请稍后再试！🐼")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理错误"""
    logger.error(f"更新 {update} 导致错误: {context.error}")

    if update and update.effective_message:
        await update.effective_message.reply_text("哎呀，出错了喵～请稍后再试！🐼")


def main() -> None:
    """启动 bot"""
    print("=" * 50)
    print("🐼 陈千语的 Telegram Bot")
    print("=" * 50)

    # 验证配置
    try:
        Config.validate()
        print("✅ 配置验证通过")
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        sys.exit(1)

    print(f"🤖 Opencode CLI: {Config.OPENCODE_CLI}")
    print("=" * 50)

    # 创建 Application
    application = Application.builder().token(Config.TELEGRAM_TOKEN).build()

    # 添加处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    # 错误处理器
    application.add_error_handler(error_handler)

    print("🚀 Bot 启动中...")
    print("📱 在 Telegram 中搜索你的 Bot 开始聊天")
    print("⚠️  按 Ctrl+C 停止")
    print("=" * 50)

    # 运行 bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
