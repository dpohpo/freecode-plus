---
name: browser-mcp-operator
description: Operate labeled Claude and ChatGPT browser tabs through Brain MCP. Use when scanning tabs, registering labels, sending messages, interrupting generation, or exporting markdown/artifacts from browser chats.
user-invocable: "true"
---

# Browser MCP Operator

Use this skill whenever the task involves live browser chat tabs that are already open in Chrome and should be controlled precisely instead of by ad-hoc GUI guessing.

## When To Use

Trigger this skill when the user wants any of these:

- talk to webpage Claude or webpage ChatGPT
- send text into an existing browser chat and press Enter
- interrupt a running generation
- export markdown or artifact content from a browser chat
- operate one of the fixed 6 chat tabs by stable label

## Hard Rule

Do not improvise with generic GUI clicking when Brain MCP browser tools are available.
Operate by stable tab `label`, not by title memory or URL guessing.

## Canonical Tool Surface

Use only these tools unless there is a concrete reason not to:

- `web_scan_tabs`
- `web_register_tab`
- `web_focus_tab`
- `web_chat_send`
- `web_chat_interrupt`
- `web_export_markdown`

## Standard Workflow

1. Call `web_scan_tabs` to see the current open chat pages.
2. If the human has already opened and logged in to the target tabs, call `web_register_tab` to bind stable labels.
3. Use `web_focus_tab` before every send or export.
4. Use `web_chat_send` with `wait_for_stop=true` unless the user explicitly wants a timed interrupt.
5. Use `web_chat_interrupt` only when generation is active.
6. Use `web_export_markdown` for artifact export. Prefer DOM extraction over browser-native download.

## Fixed Labels

When the 6-tab layout exists, prefer these labels:

- `claude-arch`
- `claude-research`
- `claude-writing`
- `gpt-review`
- `gpt-ops`
- `gpt-brain`

## Failure Handling

- If no input target is found, suspect logged-out state, wrong page, or unfinished load.
- If a tab cannot be found, re-run `web_scan_tabs`, then re-register.
- If export is too short, suspect summary export instead of artifact body.
- If interrupt returns `not_generating`, do not retry blindly; re-check state first.

## Additional Resources

- For ready-made action recipes, see [recipes.md](recipes.md).
- For a longer operator manual, see [/Volumes/金阳/Desktop/ccskill/BROWSER_MCP_OPERATOR_MANUAL.md](/Volumes/金阳/Desktop/ccskill/BROWSER_MCP_OPERATOR_MANUAL.md).
- For a single-file handoff pack, see [/Volumes/金阳/Desktop/ccskill/CLAUDE_IMPORT_ME.md](/Volumes/金阳/Desktop/ccskill/CLAUDE_IMPORT_ME.md).
