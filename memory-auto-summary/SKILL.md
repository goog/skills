---
name: memory-auto-summary
description: 自动为 memory 目录下的 markdown 文件添加主题和概要信息。使用 Python 脚本分析文件内容，提取标题、生成概要和关键词主题。用于用户要求"添加概要"、"添加主题"、"整理记忆文件"时触发。
---

# Memory 自动摘要技能

## 功能

自动为 `memory/` 目录下的 markdown 文件添加 YAML frontmatter，包含：
- **title**: 文档标题
- **topics**: 主题关键词
- **summary**: 内容概要
- **date**: 文件日期（从文件名提取）

## 触发条件

用户说：
- "添加概要"
- "添加主题"
- "整理 memory"
- "memory-auto-summary"
- 或其他要求为记忆文件添加元数据的请求

## 使用方法

### 1. 安装依赖

```bash
# 确保 Python 可用（已内置，无需安装）
pip install jieba
# default deepseek api key 自己配置一个环境变量
set LLM_API_KEY="your_api_key"
```

### 2. 运行脚本

```bash
python skills/memory-auto-summary/scripts/add_summary.py
```

或使用绝对路径：

```bash
python C:/Users/dad/.openclaw/workspace/skills/memory-auto-summary/scripts/add_summary.py
```

## 输出示例

处理后的文件会添加如下 frontmatter：

```markdown
---
title: 对话记忆
topics: 股市, 天气, 技能
summary: 用户询问了武汉天气和股市行情，助手提供了详细的信息回复...
date: 2026-03-11
---

# 对话记忆

...
```

## 注意事项

- 只会处理没有 frontmatter 的文件
- 主题关键词从预设列表中匹配（天气、股市、技能、记忆等）
- 概要取前100字
