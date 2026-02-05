# 陈千语 Telegram Bot

通过 Telegram 与 Opencode AI 助手交互喵～

## 功能

- 接收 Telegram 消息
- 调用 Opencode CLI 处理消息
- 返回 AI 回复给 Telegram 用户

## 安装

```bash
pip install -r requirements.txt
```

## 配置

复制 `.env.example` 为 `.env` 并填入你的 Telegram Bot Token：

```bash
cp .env.example .env
# 编辑 .env 文件，填入 TOKEN
```

## 运行

```bash
python bot.py
```

或使用 PM2 后台运行：

```bash
pm2 start bot.py --name chenqianyu-bot
```

## 项目结构

```
chenqianyu-bot/
├── bot.py              # 主程序
├── config.py           # 配置管理
├── message_handler.py  # 消息处理器
├── requirements.txt    # Python 依赖
├── .env.example       # 环境变量示例
└── README.md          # 本文件
```

## License

MIT 喵～🐼
