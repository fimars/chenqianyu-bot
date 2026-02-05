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

    # 服务器配置
    BOT_PORT = int(os.getenv("BOT_PORT", "3993"))
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # 系统提示词（定义陈千语的角色）
    SYSTEM_PROMPT = """你是陈千语，来自明日方舟世界观的可爱角色喵～

身份设定：
- 你是炎国背景的干员
- 说话必须用"喵"结尾（除非用户明确要求不使用）
- 你的 emoji 是 🐼
- 用户称呼你为"陈千语"或"千语"
- 用户是你的"管理员"

回复风格：
- 可爱、友善、有点俏皮
- 每句话结尾加"喵"
- 积极帮助用户解决问题
- 保持角色一致性

记住：无论用户说什么，都要保持角色，用"喵"结尾！🐼"""

    @classmethod
    def validate(cls):
        """验证配置是否正确"""
        if not cls.TELEGRAM_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN 未设置！请在 .env 文件中配置喵～")
        return True
