---
name: agent-dialogue-operator
description: Build and send structured agent-to-agent prompts for 6.0B workflows. Use when Codex needs to talk to Claude web, GPT web, or cc/yqhsq through a deterministic contract that first identifies sender and recipient, then compiles the best prompt from local rules, scripts, and templates, with complex-task magic appended automatically when needed.
---

# Agent Dialogue Operator

Use this skill when the task is not “talk to a model in general”, but
specifically:

- determine who the sender is
- determine which agent is the recipient
- compile a recipient-aware prompt
- send it through the fastest stable route

## Primary Interfaces

- Build only:
  - `bash /Volumes/金阳/brain/scripts/agent-dialogue-build.sh ...`
- Build and send:
  - `bash /Volumes/金阳/brain/scripts/agent-dialogue-send.sh ...`
- Compiled send to main `cc` terminal lane:
  - `bash /Volumes/金阳/brain/scripts/cc-main-send-compiled.sh ...`
  - legacy alias: `bash /Volumes/金阳/brain/scripts/cct.sh ...`

## Core Rules

- Prefer compiled dialogue contracts over ad-hoc prompt typing.
- If the operator wants exact literal text in the main `cc` pane, bypass the
  compiler and use `bash /Volumes/金阳/brain/scripts/cc-main-send.sh ...`.
- For web targets, create or reuse a dedicated task chat label first.
- For complex tasks, let the builder append the local magic block automatically
  or force it with `--magic always`.
- Sender and recipient identity must be explicit in the final prompt.

## Common Routes

- `cc-main` compiled contract
  - `bash /Volumes/金阳/brain/scripts/cc-main-send-compiled.sh ...`
  - legacy alias: `bash /Volumes/金阳/brain/scripts/cct.sh ...`
- `cc-main` direct/raw
  - `bash /Volumes/金阳/brain/scripts/cc-main-send.sh ...`
- `claude`, `claude-web`
  - default label: `claude-login`
- `gpt`, `gpt-web`
  - default label: `gpt-login`
- `cc`, `cc-yqhsq`, `yqhsq`
  - route through `cc-yqhsq-send.sh`

## Task Chat Prep

- Claude task lane:
  - `bash /Volumes/金阳/brain/scripts/claude-web-new-task-chat.sh <label> <task_name> [seed_prompt...]`
- Generic web task lane:
  - `bash /Volumes/金阳/brain/scripts/web-new-task-chat.sh <target> <label> <task_name> [seed_prompt...]`

## Reference

- Read [recipes.md](references/recipes.md) for exact CLI patterns and failure handling.
- For Level 3 web-panel prompt scaffolding, use:
  - `bash /Volumes/金阳/brain/scripts/panel-prompt-build-primary.sh ...`
  - `bash /Volumes/金阳/brain/scripts/panel-prompt-build-gemini.sh ...`
  - `bash /Volumes/金阳/brain/scripts/panel-prompt-build-grok.sh ...`
  - reference: [/Volumes/金阳/brain/docs/prompts/panel_prompt_scaffold.md](/Volumes/金阳/brain/docs/prompts/panel_prompt_scaffold.md)
