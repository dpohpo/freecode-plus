---
name: cct
description: Send compiled text to the Claude Code main agent in tmux. Use when the user writes `$cct ...` and wants Codex to compile a 6.0B dialogue prompt first, then inject it into the main Claude Code pane and press Enter. For exact literal text, use `cc-main-send.sh` instead. If the payload starts with `/`, pass it through raw so Claude Code slash commands and skills still work.
---

# CCT

Use this skill when the user wants to talk to the Claude Code main agent rather
than the active yqhsq pane.

## Primary Interface

- `bash /Volumes/金阳/brain/scripts/cct.sh "message"`
- `bash /Volumes/金阳/brain/scripts/cc-main-send-compiled.sh "message"`
- For weak agents that must choose a lane explicitly:
  - `bash /Volumes/金阳/brain/scripts/cc-safe-send.sh main-compiled "message"`

## Core Rules

- Treat the text after `$cct` as the task body to compile, not as a guaranteed
  byte-for-byte raw payload.
- Default to compiled 6.0B dialogue prompts by routing through:
  - `bash /Volumes/金阳/brain/scripts/agent-dialogue-build.sh ...`
- Then inject the compiled prompt into the main Claude Code pane with:
  - `bash /Volumes/金阳/brain/scripts/cc-main-send.sh ...`
- If the user wants exact literal text in the main Claude Code pane, do not use
  `cct.sh`. Use `bash /Volumes/金阳/brain/scripts/cc-main-send.sh ...`.
- If the first non-space character is `/`, do not wrap it in a dialogue
  contract. Send it raw so Claude Code slash commands and skills keep their
  native behavior.
- Target the single-pane main Claude Code window, not the `五神` team panes.

## Verification

- Dry-run main-pane resolution with:
  - `bash /Volumes/金阳/brain/scripts/cc-main-send.sh --dry-run "ping"`
- Send a real message with:
  - `bash /Volumes/金阳/brain/scripts/cc-main-send-compiled.sh "请确认收到"`
