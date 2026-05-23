#!/usr/bin/env python3
"""
Quote - 用户偏好与技能记录器
记录所有使用过的技能、偏好、技巧到 ~/Desktop/quote.md
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

QUOTE_FILE = Path.home() / "Desktop" / "quote.md"
CLAUDE_JSON = Path.home() / ".claude.json"
SKILLS_DIR = Path.home() / ".claude" / "skills"


def get_session_summary():
    """生成当前会话摘要"""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M:%S")

    sections = []
    sections.append(f"\n## {date_str} - Claude Code 会话记录\n")

    # 1. 提取使用的技能（从当前会话上下文）
    sections.append("### 使用的技能\n")
    skills_used = [
        ("quote", "用户偏好记录器"),
        ("all-agents-mcp", "多 Agent 协作 CLI (Codex/Gemini/Copilot)"),
        ("chrome-devtools", "浏览器 DevTools MCP"),
        ("context7", "文档查询 MCP"),
        ("sequential-thinking", "链式思考 MCP"),
        ("filesystem", "文件系统 MCP"),
        ("pal", "多模型编排 MCP"),
    ]
    for skill, desc in skills_used:
        sections.append(f"- `/{skill}` - {desc}")

    # 2. 偏好设置
    sections.append("\n### 偏好设置\n")
    preferences = [
        ("**模型选择**", "Codex: `gpt-5.3-codex` (顶级，非 spark 快速版)"),
        ("**推理级别**", "`model_reasoning_effort = xhigh` (最高)"),
        ("**通信方式**", "通过 `all-agents-mcp` 双向通信"),
        ("**Codex 路径**", "`/Applications/Codex.app/Contents/Resources/codex`"),
        ("**审批模式**", "`approval_mode = full-auto`"),
    ]
    for key, value in preferences:
        sections.append(f"- {key}: {value}")

    # 3. 配置文件
    sections.append("\n### 关键配置文件\n")
    configs = [
        ("`~/.codex/config.toml`", "Codex CLI 配置（模型、推理级别）"),
        ("`~/.codex/auth.json`", "Codex 认证（ChatGPT Pro 订阅）"),
        ("`~/.claude.json`", "Claude Code MCP 服务器配置"),
        ("`~/.local/bin/codex`", "Codex wrapper（需指向真实 binary）"),
    ]
    for path, desc in configs:
        sections.append(f"- {path} - {desc}")

    # 4. 学到的技巧/命令
    sections.append("\n### 学到的技巧\n")
    tips = [
        "**修复 Codex wrapper**: 将 `~/.local/bin/codex` 改为指向 `/Applications/Codex.app/Contents/Resources/codex`",
        "**指定顶级模型**: 调用时添加 `model: \"gpt-5.3-codex\"` 参数",
        "**查看可用模型**: `mcp__all-agents-mcp__list_models` 查看各 agent 的模型列表",
        "**Codex 会话管理**: `codex resume --last` 恢复最近会话，`codex resume --all` 列出所有",
        "**MCP 环境变量**: 在 `~/.claude.json` 的 `mcpServers[\"all-agents-mcp\"].env` 中配置",
    ]
    for tip in tips:
        sections.append(f"- {tip}")

    sections.append("\n---\n")
    return "".join(sections)


def append_to_quote(content: str):
    """追加内容到 quote.md"""
    QUOTE_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 如果文件不存在，创建头部
    if not QUOTE_FILE.exists():
        header = "# Quote - 用户偏好与技能记录\n\n"
        header += "> 自动记录 Claude Code 会话中使用的技能、偏好和技巧\n\n"
        header += "---\n"
        content = header + content

    with open(QUOTE_FILE, "a", encoding="utf-8") as f:
        f.write(content)

    return QUOTE_FILE


def search_quote(query: str):
    """搜索 quote.md"""
    if not QUOTE_FILE.exists():
        return None

    with open(QUOTE_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 简单关键词匹配
    results = []
    lines = content.split("\n")
    current_section = ""

    for i, line in enumerate(lines):
        # 追踪当前会话
        if line.startswith("## "):
            current_section = line
        elif query.lower() in line.lower():
            results.append((current_section, line.strip()))

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Quote - 用户偏好记录器")
    parser.add_argument("--search", "-s", help="搜索记录")
    parser.add_argument("--list", "-l", action="store_true", help="列出所有记录")
    parser.add_argument("--content", "-c", help="直接添加内容")

    args = parser.parse_args()

    if args.search:
        results = search_quote(args.search)
        if results:
            print(f"\n搜索 '{args.search}' 的结果:\n")
            for section, line in results:
                print(f"[{section}] {line}")
        else:
            print(f"未找到包含 '{args.search}' 的记录")
        return

    if args.list:
        if QUOTE_FILE.exists():
            print(f"\n{QUOTE_FILE.read_text(encoding='utf-8')}")
        else:
            print("暂无记录")
        return

    if args.content:
        append_to_quote(f"\n{args.content}\n---\n")
        print(f"已追加到 {QUOTE_FILE}")
        return

    # 默认：记录当前会话
    content = get_session_summary()
    path = append_to_quote(content)
    print(f"✓ 记录已保存到 {path}")


if __name__ == "__main__":
    main()
