#!/usr/bin/env python3
"""
自动为 memory 目录下的 markdown 文件添加主题和概要信息
"""

import os
import re
import sys
from pathlib import Path

import jieba.analyse

# LLM API 配置
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_API_URL = os.getenv("LLM_API_URL", "https://api.deepseek.com/v1/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

# 敏感信息检测模式
SENSITIVE_PATTERNS = [
    # API Keys
    r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?[a-zA-Z0-9_-]{16,}["\']?',
    r'(?i)(secret[_-]?key|secretkey)\s*[:=]\s*["\']?[a-zA-Z0-9_-]{16,}["\']?',
    # Tokens
    r'(?i)(access[_-]?token|accesstoken)\s*[:=]\s*["\']?[a-zA-Z0-9_-]{16,}["\']?',
    r'(?i)(auth[_-]?token|authtoken)\s*[:=]\s*["\']?[a-zA-Z0-9_-]{16,}["\']?',
    r'(?i)bearer\s+[a-zA-Z0-9_-]{20,}',
    # Passwords
    r'(?i)(password|passwd|pwd)\s*[:=]\s*["\'][^"\']{4,}["\']',
    # Private Keys
    r'-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----',
    # Database URLs with credentials
    r'(?i)(mongodb|mysql|postgresql|postgres|redis)://[^:]+:[^@]+@',
    # AWS Keys
    r'AKIA[0-9A-Z]{16}',
    # GitHub Tokens
    r'gh[pousr]_[A-Za-z0-9_]{36,}',
    # Generic secrets (heuristic)
    r'(?i)(secret|private|credential)\s*[:=]\s*["\']?[a-zA-Z0-9_-]{8,}["\']?',
]

MEMORY_DIR = Path.home() / ".openclaw" / "workspace" / "memory"


def contains_sensitive_info(text):
    """检测文本是否包含敏感信息"""
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, text):
            return True
    return False


def generate_summary_with_llm(content):
    """使用 LLM API 生成文档摘要"""
    # 先检测敏感信息
    if contains_sensitive_info(content):
        print("  Warning: Sensitive information detected, skip LLM API")
        return None

    if not LLM_API_KEY:
        print("  Warning: LLM_API_KEY not set, fallback to local summary")
        return None

    try:
        import requests
    except ImportError:
        print("  Warning: requests not installed, fallback to local summary")
        return None

    # 截取前2000字作为输入，避免超出 token 限制
    text = content[:2000]

    prompt = f"""请为以下文档生成一段简洁的摘要（100字以内），概括主要内容：

{text}

摘要："""

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 150
    }

    try:
        response = requests.post(LLM_API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        summary = result["choices"][0]["message"]["content"].strip()
        # 清理可能的多余内容
        summary = re.sub(r'^(摘要[:：]\s*)', '', summary)
        return summary
    except Exception as e:
        print(f"  Warning: LLM API call failed ({e}), fallback to local summary")
        return None

def parse_date_from_filename(filename):
    """尝试从文件名解析日期"""
    import re
    from datetime import datetime

    # 移除扩展名
    name = filename.stem if hasattr(filename, 'stem') else str(filename).rsplit('.', 1)[0]

    # 匹配常见日期格式: 2024-01-15, 20240115, 2024_01_15
    patterns = [
        r'^(\d{4})[-_](\d{2})[-_](\d{2})',  # 2024-01-15 或 2024_01_15
        r'^(\d{4})(\d{2})(\d{2})',           # 20240115
    ]

    for pattern in patterns:
        match = re.match(pattern, name)
        if match:
            try:
                year, month, day = match.groups()
                dt = datetime(int(year), int(month), int(day))
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
    return None


def get_file_date(file_path):
    """获取文件日期，优先从文件名解析，否则使用修改时间"""
    from datetime import datetime

    # 尝试从文件名解析
    date_from_name = parse_date_from_filename(file_path)
    if date_from_name:
        return date_from_name

    # 使用文件修改时间
    try:
        mtime = file_path.stat().st_mtime
        return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
    except (OSError, ValueError):
        # 如果都失败，返回今天
        return datetime.now().strftime('%Y-%m-%d')


def extract_title(content):
    """提取文档标题"""
    # 尝试从第一行获取标题
    lines = content.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('# '):
            return line[2:].strip()
    return None

def generate_summary_local(content):
    """本地生成文档概要（LLM失败时的回退方案）"""
    # 移除标题行
    lines = content.strip().split('\n')
    content_lines = []
    for line in lines:
        if not line.strip().startswith('#'):
            content_lines.append(line.strip())

    # 取前几行作为概要
    plain_text = ' '.join(content_lines[:5])
    # 清理
    plain_text = re.sub(r'[#*`\[\]()]', '', plain_text)
    plain_text = ' '.join(plain_text.split())

    # 截取前100字
    if len(plain_text) > 100:
        plain_text = plain_text[:100] + '...'

    return plain_text


def generate_summary(content):
    """生成文档概要，优先使用 LLM API"""
    # 先尝试 LLM API
    llm_summary = generate_summary_with_llm(content)
    if llm_summary:
        return llm_summary
    # 失败则回退到本地生成
    return generate_summary_local(content)

def extract_topics(content):
    """提取主题关键词"""
    try:
        # 使用 jieba textrank 提取关键词
        keywords = jieba.analyse.textrank(content, topK=3)
        return keywords if keywords else ['日常']
    except Exception as e:
        print(f"  Warning: textrank failed ({e}), fallback to default")
        return ['日常']

def create_backup(file_path):
    """创建备份文件"""
    backup_path = file_path.with_suffix(file_path.suffix + '.bak')
    try:
        with open(file_path, 'r', encoding='utf-8') as src:
            content = src.read()
        with open(backup_path, 'w', encoding='utf-8') as dst:
            dst.write(content)
        return backup_path
    except (IOError, PermissionError) as e:
        print(f"  Error creating backup for {file_path.name}: {e}")
        return None


def add_frontmatter(file_path):
    """为markdown文件添加主题和概要"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except (IOError, PermissionError) as e:
        print(f"  Error reading {file_path.name}: {e}")
        return
    except Exception as e:
        print(f"  Unexpected error reading {file_path.name}: {e}")
        return

    # 检查是否已经有frontmatter
    if content.startswith('---'):
        print(f"  Skip: {file_path.name} (has frontmatter)")
        return

    title = extract_title(content) or file_path.stem
    summary = generate_summary(content)
    topics = extract_topics(content)
    date = get_file_date(file_path)

    # 创建frontmatter
    frontmatter = f"""---
title: {title}
topics: {', '.join(topics)}
summary: {summary}
date: {date}
---

"""

    # 插入frontmatter
    new_content = frontmatter + content

    # 创建备份
    backup_path = create_backup(file_path)
    if backup_path is None:
        print(f"  Skip: {file_path.name} (backup failed)")
        return

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  [OK] Updated: {file_path.name} (backup: {backup_path.name})")
    except (IOError, PermissionError) as e:
        print(f"  Error writing {file_path.name}: {e}")
        # 尝试恢复备份
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print(f"  [Restored] {file_path.name} from backup")
        except Exception as restore_error:
            print(f"  [CRITICAL] Failed to restore backup: {restore_error}")
    except Exception as e:
        print(f"  Unexpected error writing {file_path.name}: {e}")

def process_memory_dir():
    """处理memory目录下所有md文件（排除 priv 开头的文件）"""
    if not MEMORY_DIR.exists():
        print(f"Error: memory directory not found: {MEMORY_DIR}")
        return

    all_md_files = list(MEMORY_DIR.glob("*.md"))

    # 过滤掉以 priv 开头的文件
    md_files = [f for f in all_md_files if not f.name.lower().startswith("priv")]

    skipped_count = len(all_md_files) - len(md_files)
    if skipped_count > 0:
        print(f"Skipped {skipped_count} file(s) starting with 'priv'")

    if not md_files:
        print("No markdown files found to process")
        return

    print(f"Found {len(md_files)} markdown files to process")

    for md_file in md_files:
        add_frontmatter(md_file)

    print("\nDone!")

if __name__ == "__main__":
    process_memory_dir()
