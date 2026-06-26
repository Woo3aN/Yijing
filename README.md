# 易经占卜 🏯

一款 Windows 桌面易经算卦软件。输入问题 → 起卦 → 查看易经原文 → AI 深度解读。

> 面向计算机大一学生，源码即文档，简单直白。

## 功能

- 🔮 **两种起卦方式**：三铜钱法（逐爻动画） / 随机数法
- 📖 **完整易经原文**：64 卦卦辞、彖传、大象传、爻辞、小象传
- 🧓 **朱熹断卦规则**：7 条规则自动判定变爻断法
- 🤖 **AI 深度解读**：支持 DeepSeek / 通义千问 / 智谱 GLM / GPT / Claude + 自定义
- 📋 **历史记录**：搜索、详情、删除、一键清空

## 快速开始

### 下载即用

下载 `易经占卜.exe`（见 [Releases](../../releases)），双击运行。

### 开发者

```bash
git clone https://github.com/你的用户名/yijing.git
cd yijing
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 语言 | Python 3.11+ |
| GUI | tkinter + ttkbootstrap |
| 数据库 | SQLite（历史记录） |
| AI | openai SDK（兼容 DeepSeek 等） |
| 打包 | PyInstaller → 单文件 exe |

## 项目结构

```
src/
├── main.py              ← 入口
├── ui/                  ← 三个标签页
│   ├── divination_page.py
│   ├── history_page.py
│   └── settings_page.py
├── core/                ← 起卦算法 + 卦象加载
│   ├── divination.py
│   └── text_loader.py
├── ai/                  ← AI 客户端
│   └── llm_client.py
├── storage/             ← SQLite + 设置
│   ├── history_db.py
│   └── app_settings.py
└── data/                ← 64 卦 JSON 数据
    └── hexagrams.json
```

## 安全说明

- API 密钥仅保存在你本地 `%APPDATA%/Yijing/settings.json`
- 不上传任何服务器
- 《周易》原文为公共领域古典文献

## 许可

MIT
