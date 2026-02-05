"""
配置管理模块喵～
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """Bot 配置"""

    # Telegram Bot Token
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    # Opencode CLI 配置
    OPENCODE_CLI = os.getenv("OPENCODE_CLI", "opencode")

    # 安全设置 - 只允许特定用户访问
    ALLOWED_USER_ID = os.getenv("ALLOWED_USER_ID")

    # 服务器配置
    BOT_PORT = int(os.getenv("BOT_PORT", "3993"))
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # AGENTS.md 配置目录
    AGENTS_CONFIG_DIR = os.getenv(
        "AGENTS_CONFIG_DIR", os.path.expanduser("~/.config/opencode/")
    )

    @classmethod
    def validate(cls):
        """验证配置是否正确"""
        if not cls.TELEGRAM_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN 未设置！请在 .env 文件中配置喵～")
        return True
