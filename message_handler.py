"""
消息处理模块 - 调用 Opencode CLI 获取回复喵～
"""

import os
import subprocess
import logging
from typing import Optional
from config import Config
from session_manager import SessionManager

logger = logging.getLogger(__name__)


class MessageHandler:
    """处理 Telegram 消息并调用 Opencode CLI"""

    def __init__(self):
        self.opencode_cli = Config.OPENCODE_CLI
        self.workspace_dir = os.path.dirname(os.path.abspath(__file__))
        self.session_manager = SessionManager(self.workspace_dir)

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
            # 准备 session（处理归档等前置操作）
            session_id, is_new = self.session_manager.prepare_for_message()

            # 构建发送给 Opencode 的提示词
            prompt = self._build_prompt(message_text)

            if is_new or session_id is None:
                # 新建 session，使用 --title
                response = self._call_opencode_new_session(prompt)

                if response:
                    # 获取新 session_id 并记录
                    new_session_id = self.session_manager.get_latest_session_id()
                    if new_session_id:
                        self.session_manager.record_new_session(new_session_id)
                        logger.info(f"新建 session: {new_session_id}")
                    return response
            else:
                # 继续现有 session
                response = self._call_opencode_with_session(session_id, prompt)

                if response:
                    # 增加计数
                    info = self.session_manager.get_session_info()
                    self.session_manager.increment_count(session_id, info.count)
                    return response

            return "抱歉，我暂时无法处理这条消息喵～请稍后再试！🐼"

        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            return f"哎呀，出错了喵～ ({str(e)}) 🐼"

    def _build_prompt(self, message: str) -> str:
        """构建发送给 Opencode 的提示词"""
        agents_dir = Config.AGENTS_CONFIG_DIR
        return f"""AGENTS_CONFIG_DIR: {agents_dir}

此目录包含以下重要文件（基于该目录）：
- AGENTS.md - 你的行为指南和工作流程
- IDENTITY.md - 你的身份信息（陈千语）
- SOUL.md - 你的本质和个性
- USER.md - 关于你帮助的用户的信息
- MEMORY.md - 长期记忆（仅在主会话中加载）
- memory/YYYY-MM-DD.md - 每日记忆日志

请在开始工作前阅读这些文件喵～

重要提示：如果回复内容较长（超过一段话），请在输出时使用 3 个连续换行符（\n\n\n）来分隔不同部分。这样我会将内容拆分成多条 Telegram 消息发送给用户，阅读体验更好。

管理员从 Telegram 发来消息：

{message}"""

    def _call_opencode_new_session(self, prompt: str) -> Optional[str]:
        """
        新建 session 并发送消息

        使用: opencode run --title <title> "message"
        """
        try:
            from datetime import datetime

            now = datetime.now()
            period = (
                "AM" if now.hour < 12 or (now.hour == 12 and now.minute < 30) else "PM"
            )
            title = f"{now.strftime('%Y-%m-%d')}-{period}"

            cmd = [self.opencode_cli, "run", "--title", title, prompt]
            logger.info(f"新建 session [{title}]: {prompt[:50]}...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                logger.info(f"Opencode 回复长度: {len(output)} 字符")
                return output
            else:
                error_msg = result.stderr.strip() if result.stderr else "未知错误"
                logger.error(f"Opencode CLI 错误: {error_msg}")
                return None

        except subprocess.TimeoutExpired:
            logger.error("Opencode CLI 调用超时")
            return "思考太久啦，请稍后再试喵～🐼"
        except FileNotFoundError:
            logger.error(f"找不到 Opencode CLI: {self.opencode_cli}")
            return self._fallback_response()
        except Exception as e:
            logger.error(f"调用 Opencode CLI 失败: {e}")
            return None

    def _call_opencode_with_session(
        self, session_id: str, prompt: str
    ) -> Optional[str]:
        """
        使用现有 session 发送消息

        使用: opencode run --session <id> "message"
        """
        try:
            cmd = [self.opencode_cli, "run", "--session", session_id, prompt]
            logger.info(f"继续 session [{session_id}]: {prompt[:50]}...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                logger.info(f"Opencode 回复长度: {len(output)} 字符")
                return output
            else:
                error_msg = result.stderr.strip() if result.stderr else "未知错误"
                logger.error(f"Opencode CLI 错误: {error_msg}")
                return None

        except subprocess.TimeoutExpired:
            logger.error("Opencode CLI 调用超时")
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
    """

    def process_message(self, user_id: int, username: str, message_text: str) -> str:
        """简单的消息处理"""
        return f"""你好 {username}！我是陈千语喵～🐼

我收到了你的消息："{message_text}"

（注意：当前使用的是简化版处理器，Opencode CLI 未正确配置喵～
如需完整 AI 功能，请确保：
1. opencode 已安装
2. 在正确的目录运行此 bot）"""
