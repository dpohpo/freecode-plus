---
name: brain-web-operator
description: Operate labeled browser chat tabs through Brain MCP with low-latency, low-drift actions. Use when Codex needs to scan open debug-browser tabs, register stable labels, focus a specific Claude/ChatGPT/Gemini/Grok tab, send a message, interrupt a running generation, export markdown/artifact content, or switch Claude web models through local shell wrappers.
---

# Brain Web Operator

## Overview

Use the narrow Brain MCP browser tool surface instead of generic GUI control.
Work by stable tab labels, not by guessing from URL or title.

## Quick Start

1. Call `web_scan_tabs` to discover the current browser pages.
2. Call `web_register_tab` once per prepared tab to bind a stable `label`.
3. Use `web_focus_tab` before actions that depend on the visible page.
4. Use `web_chat_send` for one message at a time.
5. Use `web_chat_interrupt` only when the page is already generating.
6. Use `web_export_markdown` for artifact or markdown extraction.
7. For repeated browser workspace and Claude model changes, prefer the dedicated shell wrappers in `/Volumes/金阳/brain/scripts`.

## Rules

- Register tabs once, then operate only by `label`.
- Keep one main purpose/topic per tab.
- Do not send messages to the same tab from two agents at the same time.
- Prefer DOM export over browser-native downloads.
- Treat unexpectedly short exports as a routing/view problem, not as success.

## Decision Guide

- Need to discover what pages exist:
  - Use `web_scan_tabs`.
- Need to bind a human-prepared tab to a stable identity:
  - Use `web_register_tab`.
- Need to switch to a known work lane:
  - Use `web_focus_tab`.
- Need to talk to a chat page:
  - Use `web_chat_send`.
- Need to send a long structured prompt with strict formatting:
  - Prefer file-based send wrappers in `/Volumes/金阳/brain/scripts`.
  - Do not inline huge multi-section prompts into shell-quoted one-liners.
- Need to stop a long generation:
  - Use `web_chat_interrupt`.
- Need a local `.md` from a browser artifact:
  - Use `web_export_markdown`.
  - On Claude chat tabs without an explicit artifact target, export now uses a
    structured answer extractor instead of whole-page text.
- Need to bring up the standard five-tab workspace:
  - Use `bash /Volumes/金阳/brain/scripts/agent-browser-up.sh`.
- Need to send a long prompt from a file without shell flattening:
  - Use `bash /Volumes/金阳/brain/scripts/web-chat-send-file.sh <label> <message_file>`.
  - On Claude tabs, this path now uses a host-specific blank-line preservation
    strategy; prefer it over ad hoc inline send for any structured review
    prompt.
- Need to open a fresh task lane and send the first-round Level 3 prompt from a file:
  - Use `bash /Volumes/金阳/brain/scripts/panel-send-primary.sh <target> <label> <task_name> <prompt_file>`.
- Need to restart the managed browser profile and restore the four-tab workspace:
  - Use `bash /Volumes/金阳/brain/scripts/agent-browser-restart.sh`.
- Need to switch Claude web from Sonnet to Opus (or another supported model):
  - Use `bash /Volumes/金阳/brain/scripts/claude-web-model-set.sh <model> [label]`.
- Need to open multiple fresh Claude chats with stable system labels:
  - Use `bash /Volumes/金阳/brain/scripts/claude-web-new-chat.sh <label> [purpose] [topic]`.
- Need one dedicated Claude chat per specific task:
  - Use `bash /Volumes/金阳/brain/scripts/claude-web-new-task-chat.sh <label> <task_name> [seed_prompt...]`.
- Need two dedicated Claude task chats and then repeated switching:
  - Use `bash /Volumes/金阳/brain/scripts/claude-web-task-pair.sh <label_a> <task_a> <label_b> <task_b> [rounds] [sleep_s]`.
- Need to rename a Claude system label:
  - Use `bash /Volumes/金阳/brain/scripts/claude-web-relabel.sh <old_label> <new_label>`.
- Need to bounce between two Claude chats repeatedly:
  - Use `bash /Volumes/金阳/brain/scripts/claude-web-switch-loop.sh <label_a> <label_b> [rounds] [sleep_s]`.

## Artifact Export Guidance

- For Claude artifacts, usually provide `artifact_title`.
- For Claude artifacts, usually keep `open_code_view=True`.
- Provide a `start_marker` that matches the first true heading of the document.
- Keep `end_marker="Share"` unless the page layout changes.

## References

- Read [recipes.md](references/recipes.md) for exact usage patterns, export recipes, and failure handling.

Keep this skill thin. The browser tool surface is intentionally narrow because low ambiguity and low latency matter more here than broad GUI flexibility.
