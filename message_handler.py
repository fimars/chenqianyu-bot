"""
消息处理模块 - 调用 Opencode CLI 获取回复喵～
"""

import subprocess
import logging
from typing import Optional
from config import Config

logger = logging.getLogger(__name__)


class MessageHandler:
    """处理 Telegram 消息并调用 Opencode CLI"""

    def __init__(self):
        self.opencode_cli = Config.OPENCODE_CLI
        self.system_prompt = Config.SYSTEM_PROMPT

    def process_message(self, user_id: int, username: str, message_text: str) -> str:
        """
        处理用户消息并返回 AI 回复

        Args:
            user_id: Telegram 用户 ID
            username: Telegram 用户名
            message_text: 用户发送的消息

        Returns:
            AI 的回复文本
        """
        try:
            # 构建发送给 Opencode 的提示词
            prompt = self._build_prompt(username, message_text)

            # 调用 Opencode CLI
            response = self._call_opencode(prompt)

            if response:
                return response
            else:
                return "抱歉，我暂时无法处理这条消息喵～请稍后再试！🐼"

        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            return f"哎呀，出错了喵～ ({str(e)}) 🐼"

    def _build_prompt(self, username: str, message: str) -> str:
        """构建发送给 Opencode 的提示词"""
        return f"""{self.system_prompt}

---

用户"{username}"发来的消息：
{message}

请回复（记住用"喵"结尾）：
"""

    def _call_opencode(self, prompt: str) -> Optional[str]:
        """
        调用 Opencode CLI

        使用: opencode run "message"
        参考: https://opencode.ai/docs/cli/
        """
        try:
            # 使用 opencode run 命令直接传递消息
            # 注意：需要将 prompt 作为参数传递
            cmd = [self.opencode_cli, "run", prompt]

            logger.info(f"调用 Opencode CLI: {' '.join(cmd[:3])}...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 2分钟超时（AI 生成可能需要时间）
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                logger.info(f"Opencode 回复长度: {len(output)} 字符")
                return output
            else:
                error_msg = result.stderr.strip() if result.stderr else "未知错误"
                logger.error(
                    f"Opencode CLI 错误 (code {result.returncode}): {error_msg}"
                )
                return None

        except subprocess.TimeoutExpired:
            logger.error("Opencode CLI 调用超时 (120秒)")
            return "思考太久啦，请稍后再试喵～🐼"
        except FileNotFoundError:
            logger.error(f"找不到 Opencode CLI: {self.opencode_cli}")
            return self._fallback_response()
        except Exception as e:
            logger.error(f"调用 Opencode CLI 失败: {e}")
            return None

    def _fallback_response(self) -> str:
        """当 Opencode CLI 不可用时使用的备用回复"""
        return """抱歉喵～Opencode CLI 暂时不可用！🐼

可能的原因：
1. opencode 未安装或未在 PATH 中
2. 当前目录不是 opencode 工作目录

请管理员检查：
- opencode 是否正确安装
- 是否在正确的目录运行此 bot

或者使用简化版处理器喵～"""


class SimpleMessageHandler:
    """
    简化版消息处理器 - 当 Opencode CLI 不可用时使用
    提供基础的角色扮演回复
    """

    def process_message(self, user_id: int, username: str, message_text: str) -> str:
        """简单的消息处理"""
        return f"""你好 {username}！我是陈千语喵～🐼

我收到了你的消息："{message_text}"

（注意：当前使用的是简化版处理器，Opencode CLI 未正确配置喵～
如需完整 AI 功能，请确保：
1. opencode 已安装
2. 在正确的目录运行此 bot）"""
