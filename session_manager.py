"""
Session 管理模块 - Unix 哲学：文件即状态喵～

sessions/ 目录结构：
├── 2025-02-05-AM      (session_id count)
└── 2025-02-05-PM      (session_id count)

每行格式：session_id count
满 10 次后自动归档到 memory
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# 会话次数上限
MESSAGE_LIMIT = 10


@dataclass
class SessionInfo:
    """Session 状态信息"""

    session_id: Optional[str]  # None 表示需要新建
    count: int  # 当前计数
    need_archive: bool  # 是否需要先归档
    archive_session_id: Optional[str] = None  # 需要归档的 session


class SessionManager:
    """管理 Opencode Sessions"""

    def __init__(self, workspace_dir: str):
        self.workspace_dir = Path(workspace_dir)
        self.sessions_dir = self.workspace_dir / "sessions"
        self.sessions_dir.mkdir(exist_ok=True)

        # 确保 memory 软链接存在
        self._ensure_memory_link()

    def _ensure_memory_link(self):
        """确保 memory 软链接指向 ~/.config/opencode/memory"""
        memory_link = self.workspace_dir / "memory"
        memory_target = Path.home() / ".config" / "opencode" / "memory"

        # 确保目标目录存在
        memory_target.mkdir(parents=True, exist_ok=True)

        # 创建或修复软链接
        if memory_link.exists() or memory_link.is_symlink():
            if not memory_link.is_symlink() or memory_link.readlink() != memory_target:
                memory_link.unlink()
                memory_link.symlink_to(memory_target)
                logger.info(f"更新 memory 软链接: {memory_target}")
        else:
            memory_link.symlink_to(memory_target)
            logger.info(f"创建 memory 软链接: {memory_target}")

    def _get_period_file(self) -> Path:
        """获取当前时间段的 session 文件路径"""
        now = datetime.now()
        period = "AM" if now.hour < 12 or (now.hour == 12 and now.minute < 30) else "PM"
        filename = f"{now.strftime('%Y-%m-%d')}-{period}"
        return self.sessions_dir / filename

    def _get_memory_file(self) -> Path:
        """获取今天的 memory 文件路径"""
        now = datetime.now()
        memory_dir = Path.home() / ".config" / "opencode" / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        return memory_dir / f"{now.strftime('%Y-%m-%d')}.md"

    def _read_last_session(self, period_file: Path) -> Optional[Tuple[str, int]]:
        """读取最后一行 session 信息"""
        if not period_file.exists():
            return None

        try:
            with open(period_file, "r") as f:
                lines = f.readlines()
                if not lines:
                    return None
                last_line = lines[-1].strip()
                if not last_line:
                    return None
                parts = last_line.split()
                if len(parts) >= 2:
                    return parts[0], int(parts[1])
                return None
        except Exception as e:
            logger.error(f"读取 session 文件失败: {e}")
            return None

    def get_session_info(self) -> SessionInfo:
        """
        获取当前 session 状态信息

        Returns:
            SessionInfo: 包含 session_id, count, need_archive 等信息
        """
        period_file = self._get_period_file()
        existing = self._read_last_session(period_file)

        if existing:
            session_id, count = existing
            if count < MESSAGE_LIMIT:
                # 继续使用现有 session
                return SessionInfo(
                    session_id=session_id, count=count, need_archive=False
                )
            else:
                # 满 10 次，需要先归档，然后新建
                return SessionInfo(
                    session_id=None,
                    count=count,
                    need_archive=True,
                    archive_session_id=session_id,
                )
        else:
            # 没有现有 session，需要新建
            return SessionInfo(session_id=None, count=0, need_archive=False)

    def _archive_session(self, session_id: str):
        """归档 session 到 memory"""
        memory_file = self._get_memory_file()

        archive_prompt = f"""总结这次会话(session: {session_id})的长期有用内容。
将总结追加写入文件: {memory_file}

格式随意，可以包括：
- 讨论的主题
- 做出的决策
- 完成的任务
- 有用的代码或命令

如果没有什么值得记录的，可以不写或简单写一句。"""

        try:
            cmd = ["opencode", "run", "--session", session_id, archive_prompt]
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )
            logger.info(f"已归档 session: {session_id}")
        except Exception as e:
            logger.error(f"归档 session 失败: {e}")

    def record_new_session(self, session_id: str):
        """记录新创建的 session"""
        period_file = self._get_period_file()
        with open(period_file, "a") as f:
            f.write(f"{session_id} 1\n")
        logger.info(f"记录新 session: {session_id}")

    def increment_count(self, session_id: str, current_count: int):
        """增加 session 计数"""
        period_file = self._get_period_file()
        try:
            with open(period_file, "r") as f:
                lines = f.readlines()

            # 找到对应的行并更新
            for i, line in enumerate(lines):
                parts = line.strip().split()
                if parts and parts[0] == session_id:
                    lines[i] = f"{session_id} {current_count + 1}\n"
                    break

            with open(period_file, "w") as f:
                f.writelines(lines)
        except Exception as e:
            logger.error(f"更新 session 计数失败: {e}")

    def get_latest_session_id(self) -> Optional[str]:
        """从 session list 获取当前时间段最新的 session ID"""
        from datetime import datetime

        now = datetime.now()
        period = "AM" if now.hour < 12 or (now.hour == 12 and now.minute < 30) else "PM"
        expected_title = f"{now.strftime('%Y-%m-%d')}-{period}"

        try:
            cmd = ["opencode", "session", "list"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                # 找到匹配的 session（最新的在前）
                for line in lines:
                    line = line.strip()
                    # 跳过标题行、分隔线、空行
                    if (
                        not line
                        or line.startswith("Session ID")
                        or line.startswith("─")
                    ):
                        continue
                    # 检查标题是否匹配
                    parts = line.split(maxsplit=2)
                    if len(parts) >= 3 and parts[0].startswith("ses_"):
                        title = parts[1]
                        if title == expected_title:
                            return parts[0]
        except Exception as e:
            logger.error(f"获取 session 列表失败: {e}")
        return None

    def prepare_for_message(self) -> Tuple[Optional[str], bool]:
        """
        准备发送消息，处理归档等前置操作

        Returns:
            Tuple[session_id, is_new]: session_id（None 表示需要新建）和是否新 session
        """
        info = self.get_session_info()

        if info.need_archive and info.archive_session_id:
            # 先归档满 10 次的 session
            self._archive_session(info.archive_session_id)
            return None, True

        if info.session_id:
            # 继续现有 session
            return info.session_id, False

        # 需要新建 session
        return None, True
