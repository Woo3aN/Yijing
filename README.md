# 易经占卜 🏯

一款 Windows 桌面易经算卦软件。输入问题 → 起卦 → 查看易经原文 → AI 深度解读。

> 面向计算机大一学生，源码即文档，简单直白。

## 功能

- 🔮 **两种起卦方式**：三铜钱法（逐爻动画） / 随机数法（一键生成）
- 📖 **完整易经原文**：64 卦卦辞、彖传、大象传、爻辞、小象传
- 🧓 **朱熹断卦规则**：7 条规则自动判定变爻断法
- 🤖 **AI 深度解读**：支持 DeepSeek / 通义千问 / 智谱 GLM / GPT / Claude + 自定义模型
- 📋 **历史记录**：分页浏览、关键词搜索、详情查看、删除 / 清空
- 📎 **复制导出**：一键复制卦象全文、导出为 .txt 文件
- 🎨 **主题切换**：18 个内置主题，一键切换、重启保持
- 📦 **单文件 EXE**：PyInstaller 打包，无需安装 Python

## 快速开始

### 下载即用

👉 [下载 Yijing.exe](https://github.com/Woo3aN/Yijing/releases/latest)（见 [Releases](../../releases)），双击运行。

### 开发者

```bash
git clone https://github.com/Woo3aN/Yijing.git
cd Yijing
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
| CI/CD | GitHub Actions（推送 tag 自动构建发布） |

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
