# 技术选型与架构说明

## 技术栈

| 层面 | 技术 | 版本 | 选择理由 |
|------|------|------|----------|
| 编程语言 | Python | 3.11+ | 大一主流教学语言，语法友好 |
| GUI 框架 | tkinter (标准库) | — | Python 自带，无需额外安装 |
| GUI 美化 | ttkbootstrap | ≥1.10 | 一个 pip 安装，给 tkinter 加现代 Bootstrap 风格主题 |
| 数据存储 | JSON + SQLite | 标准库 | 都内置于 Python，无需服务器 |
| AI SDK | openai | ≥1.0 | DeepSeek 完全兼容 OpenAI 接口格式 |
| 打包工具 | PyInstaller | ≥6.0 | 最成熟的 Python → exe 方案 |

## 为什么选这个方案

### 不选 Electron
- 需要 Node.js 知识，对大一学生不友好
- 打包体积 150MB+，太重
- 本项目不需要 Web 技术

### 不选 PyQt / PySide
- 功能虽强但学习曲线陡
- 打包配置复杂
- 对本项目而言杀鸡用牛刀

### 不选 C# WinForms
- 需要学 C# 和 .NET 生态
- 不利于将来可能跨平台

### 选 tkinter + ttkbootstrap 的理由
- tkinter 是 Python 标准库，装 Python 就有
- ttkbootstrap 一行代码升级外观，自带 15+ 主题
- 中文在 Windows 上原生渲染（微软雅黑）
- PyInstaller 对 tkinter 有最好的打包支持
- 学生可以看懂并修改每一行代码

## 项目架构

```
┌─────────────────────────────────────────┐
│               UI 层 (src/ui/)            │
│  main_window.py  ─ 主窗口（Notebook）    │
│  ├── divination_page.py  ─ 问卦主界面    │
│  ├── history_page.py     ─ 历史记录      │
│  └── settings_page.py    ─ 设置          │
├─────────────────────────────────────────┤
│              业务逻辑层 (src/core/)       │
│  divination.py  ─ 起卦算法               │
│  hexagram.py    ─ 卦象数据模型            │
│  text_loader.py ─ 数据加载器              │
├─────────────────────────────────────────┤
│              AI 层 (src/ai/)             │
│  llm_client.py  ─ LLM API 调用           │
├─────────────────────────────────────────┤
│              存储层 (src/storage/)        │
│  history_db.py    ─ SQLite 历史记录       │
│  app_settings.py  ─ 设置文件读写          │
├─────────────────────────────────────────┤
│              数据层 (src/data/)           │
│  hexagrams.json  ─ 64卦完整原文           │
└─────────────────────────────────────────┘
```

**依赖方向**：UI → 业务逻辑/存储/AI → 数据层
- UI 层调用下层，下层不依赖 UI
- 数据层是最底层，被所有模块引用

## 关键设计决策

### 1. 卦象数据用 JSON 而非数据库
- 64 卦是固定数据，不会变
- JSON 人类可读，容易校对
- PyInstaller 打包时自动包含
- 比 SQLite 更轻量

### 2. 历史记录用 SQLite
- 数据量可能增长（用户可能占卜很多次）
- SQLite 支持搜索、排序、分页
- Python 标准库自带，零依赖

### 3. 设置文件位置
- 路径：`%APPDATA%/Yijing/settings.json`
- 选 %APPDATA% 是 Windows 桌面应用的标准做法
- 不同用户隔离，权限安全

### 4. 起卦算法
- 三铜钱法：`random.randint(0,1)` 模拟每枚硬币，概率与真实硬币一致
- 随机数法：`random.choices([6,7,8,9], k=6)` 直接生成
- 两者用同一个 `lines_to_hexagram()` 函数判定卦象

### 5. AI 接口兼容性
- 使用 `openai` SDK，设 `base_url` 指向目标服务
- DeepSeek、通义千问、智谱 GLM 等都兼容 OpenAI 格式
- 用户可在设置中自行填入任意兼容接口地址
