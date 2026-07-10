# 易经占卜

Windows 桌面易经算卦软件。输入问题，起卦，查看周易原文，AI 深度解读。

PySide6 (Qt) 构建，支持深色/浅色双主题一键切换。

## 功能

- **两种起卦方式**：三铜钱法（逐爻动画）/ 随机数法（即时出结果）
- **64 卦完整原文**：卦辞、彖传、大象传、爻辞、小象传
- **朱熹断卦规则**：7 条规则自动判定变爻
- **AI 深度解读**：支持 DeepSeek / Qwen / GLM / GPT / Claude / MiniMax / Kimi / MiMo
- **历史记录**：分页浏览、搜索、详情、删除
- **复制导出**：一键复制结果、导出 TXT 文件
- **深色/浅色**：即时切换，圆角卡片自适应

## 快速开始

### 下载即用

下载 `Yijing.exe`（见 [Releases](https://github.com/Woo3aN/Yijing/releases)），双击运行。

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
| GUI | PySide6 (Qt) |
| 样式 | QSS 全局样式表 |
| 数据库 | SQLite |
| AI | openai SDK |
| 打包 | PyInstaller |

## 项目结构

```
src/
├── main.py              # 入口
├── ui/                  # UI 层
│   ├── main_window.py   # 主窗口 + QSS 主题
│   ├── divination_page.py
│   ├── history_page.py
│   └── settings_page.py
├── core/                # 起卦算法 + 卦象数据
│   ├── divination.py
│   ├── hexagram.py
│   └── text_loader.py
├── ai/                  # AI 客户端
│   └── llm_client.py
├── storage/             # SQLite + 设置
│   ├── history_db.py
│   └── app_settings.py
└── data/                # 64 卦 JSON
    └── hexagrams.json
```

## 安全

- API 密钥仅保存在本地 `%APPDATA%/Yijing/settings.json`
- 不上传任何服务器
- 《周易》原文为公共领域古典文献

## 许可

MIT
