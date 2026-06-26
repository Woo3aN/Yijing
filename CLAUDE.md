# CLAUDE.md — 易经占卜桌面软件

## 项目简介

一款 Windows 桌面易经算卦软件。用户输入问题 → 周易起卦 → 显示卦象和易经原文 → 可选 AI 深度解读。

- **目标用户**：计算机大一学生
- **技术栈**：Python 3.11+ / tkinter + ttkbootstrap / SQLite / openai SDK
- **交付形式**：单个 .exe 文件

## 文档索引

| 文档 | 路径 | 内容 |
|------|------|------|
| 需求规格 | [docs/requirements.md](docs/requirements.md) | 功能需求、非功能需求、范围边界 |
| 技术选型 | [docs/tech-stack.md](docs/tech-stack.md) | 技术栈理由、项目架构图、关键设计决策 |
| 设计规范 | [docs/design-spec.md](docs/design-spec.md) | UI 布局、交互流程、颜色字体、状态提示 |
| 数据格式 | [docs/data-format.md](docs/data-format.md) | hexagrams.json 结构、字段说明、查找逻辑 |
| 执行计划 | [docs/implementation-plan.md](docs/implementation-plan.md) | 10 个阶段的详细步骤和验证标准 |
| 开发日志 | [dev-logs/](dev-logs/) | 每日开发记录 |

## 工作约定

### 开发节奏
- 严格按 [执行计划](docs/implementation-plan.md) 的 10 个阶段推进
- **每次只执行一个阶段**，完成后暂停，等待用户确认再继续
- 每完成一个阶段，更新当日开发日志

### 开发日志
- 每次工作结束后，在 `dev-logs/` 下创建或更新当日 `YYYY-MM-DD.md`
- 记录：完成了什么、遇到什么问题、下一步计划

### 代码风格
- 所有注释和用户可见文本使用中文
- 变量名、函数名使用英文（Python 惯例）
- 类型注解尽量使用（帮助大一学生理解）
- 代码保持简单直白，不过度抽象

### 测试验证
- 每个阶段完成后按 [执行计划](docs/implementation-plan.md) 中的验证标准检查
- 功能必须先能跑通，再考虑优化

### 数据优先
- `hexagrams.json` 是所有功能的基础，变更需谨慎
- 修改数据结构前先更新 [数据格式文档](docs/data-format.md)

## 项目结构

```
Yijing/
├── CLAUDE.md              ← 本文件
├── docs/                  ← 项目文档
│   ├── requirements.md    ← 需求规格
│   ├── tech-stack.md      ← 技术选型
│   ├── design-spec.md     ← UI 设计规范
│   ├── data-format.md     ← 数据格式说明
│   └── implementation-plan.md ← 分步执行计划
├── dev-logs/              ← 开发日志
├── src/                   ← 源代码
│   ├── main.py            ← 入口
│   ├── ui/                ← UI 层
│   ├── core/              ← 业务逻辑
│   ├── ai/                ← AI 接口
│   ├── storage/           ← 存储层
│   └── data/              ← 数据文件
├── assets/                ← 图标等资源
└── requirements.txt       ← Python 依赖
```
