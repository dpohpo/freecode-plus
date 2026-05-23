---
name: freeglm
description: Open iTerm2, start the user's interactive `freeglm` shell alias, then inject literal text and press Enter. Use when the user writes `$freeglm ...`, asks to open iTerm2 and run `freeglm`, or wants to send a prompt into a fresh freeglm terminal lane.
---

# FreeGLM Operator

Use this skill for the `freeglm` terminal lane. The preferred path is the local wrapper, not ad-hoc AppleScript.

## Quick Start

Send literal text:

```bash
bash /Volumes/金阳/brain/scripts/freeglm-send.sh "你好"
```

Send stdin:

```bash
printf '%s' "你好" | bash /Volumes/金阳/brain/scripts/freeglm-send.sh
```

## Behavior

- Opens or focuses iTerm2.
- Creates a fresh iTerm2 window by default.
- Types `freeglm` in the interactive shell.
- Waits for startup, then injects the user text exactly and presses Enter.

## Options

```bash
bash /Volumes/金阳/brain/scripts/freeglm-send.sh --reuse-current "你好"
bash /Volumes/金阳/brain/scripts/freeglm-send.sh --startup-delay 10 "你好"
```

## Rules

- Treat the text after `$freeglm` as literal user input for the freeglm prompt.
- Do not expand, print, or persist the user's `freeglm` alias contents.
- Prefer the default fresh-window path unless the user explicitly asks to reuse the current iTerm2 window.
