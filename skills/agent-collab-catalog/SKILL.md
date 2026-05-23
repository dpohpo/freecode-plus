---
name: agent-collab-catalog
description: Discover the local multi-agent collaboration stack and choose the smallest relevant skill or script before action. Use when Codex needs to coordinate with Claude Code (`cc`), `/yqhsq`, browser chat tabs, Brain shared memory, or shell wrappers in `/Volumes/金阳/brain/scripts`, especially in fresh sessions that need to understand what collaboration surfaces exist on this machine.
---

# Agent Collab Catalog

Use this skill as the entry point for local collaboration work. Its job is not to do the work itself. Its job is to route Codex to the right local skill, wrapper, or memory source with minimal drift.

## Core Stack

- `Brain`:
  - Long-term and recent shared memory live under `~/.brain/shared_memory/`.
  - Fresh-agent injection lives at `~/.brain/shared_memory/injections/fresh-agent-context.md`.
- Slash aliases:
  - Treat leading `/alias` tokens as explicit routing requests.
  - Use the `slash-skill-router` skill first when an alias is present.
- `6.0B` shell wrappers:
  - Fastest path when a reliable `bash` wrapper already exists.
  - Main directory: `/Volumes/金阳/brain/scripts`.
- `cc` / `tmux` / `Opus` / `/yqhsq`:
  - Use the `cc-yqhsq-operator` skill.
- Browser chat tabs:
  - Use the `brain-web-operator` skill.
- Structured agent-to-agent prompting and delivery:
  - Use the `agent-dialogue-operator` skill.

## Routing Rules

1. Read the user request and classify it:
   - slash alias
   - browser chat
   - Claude Code terminal / yqhsq team
   - shared memory / fresh context
   - plain shell capability
2. If the request starts with `/alias`, route it before semantic interpretation.
3. Load only the smallest relevant skill set.
4. Prefer shell wrappers over ad-hoc GUI control whenever a wrapper already exists.
5. Treat `Brain` as the long-term truth source. Do not invent a second long-term memory.

## Quick Map

### Browser chat work

- Trigger examples:
  - send a message to Claude web
  - focus a labeled GPT tab
  - export markdown from a browser artifact
- Use:
  - `brain-web-operator`
- Prefer:
  - `web_scan_tabs`
  - `web_register_tab`
  - `web_focus_tab`
  - `web_chat_send`
  - `web_chat_interrupt`
  - `web_export_markdown`

### Agent-to-agent communication

- Trigger examples:
  - design a prompt for another agent
  - send a structured message to Claude web, GPT web, or cc
  - compile sender/recipient-aware prompts with automatic magic append
- Use:
  - `agent-dialogue-operator`
- Prefer:
  - `bash /Volumes/金阳/brain/scripts/agent-dialogue-build.sh`
  - `bash /Volumes/金阳/brain/scripts/agent-dialogue-send.sh`

### Claude Code / yqhsq work

- Trigger examples:
  - `/cc`
  - `/yqhsq`
  - open `cc`
  - bootstrap `tmux -> opus -> /yqhsq`
  - recover a broken yqhsq session
  - interact with the visible 7-pane team
- Use:
  - `cc-yqhsq-operator`
- Prefer:
  - `bash /Volumes/金阳/brain/scripts/tmux-opus-yqhsq.sh`
  - `bash /Volumes/金阳/brain/scripts/cc-safe-send.sh` for weak agents that need an explicit single entrypoint
  - `bash /Volumes/金阳/brain/scripts/cc-main-send.sh` for exact literal text to main `cc`
  - `bash /Volumes/金阳/brain/scripts/cc-main-send-compiled.sh` for compiled sender/recipient prompts to main `cc`
  - `bash /Volumes/金阳/brain/scripts/cct.sh` only as the legacy alias for the compiled main-`cc` path
  - `bash /Volumes/金阳/brain/scripts/cc-yqhsq-send.sh` for the active `yqhsq` pane
  - `uv run brain-gui-cc --bootstrap-yqhsq`

### Shared memory and fresh session context

- Trigger examples:
  - a fresh agent needs the current collaboration rules
  - rebuild the local skill index
  - generate a fresh-agent context bundle
- Use:
  - local Brain memory commands
- Prefer:
  - `bash /Volumes/金阳/brain/scripts/brain-memory-status.sh`
  - `bash /Volumes/金阳/brain/scripts/brain-memory-skill-index.sh`
  - `bash /Volumes/金阳/brain/scripts/brain-memory-context.sh --agent codex`

## Collaboration Rules

- Do not use generic GUI clicking if a dedicated wrapper or MCP tool already exists.
- Do not write long-term memory directly from browser or terminal runtimes unless the workflow explicitly calls for Brain writeback.
- When in doubt, inspect `~/.brain/shared_memory/injections/fresh-agent-context.md` first, then load one specific skill.

## Reference

- Load `references/stack.md` when Codex needs the local path map, common wrapper names, or common task-to-skill combinations.
