---
name: opencode-window
description: Fast raw messaging to the interactive OpenCode chat window through a deterministic bash bridge. Use when the user wants Codex to quickly tell OpenCode something, send a short command/message to OpenCode, or asks to talk to the OpenCode window without compiled coordination.
---

# OpenCode Window

Use this skill for fast Codex -> OpenCode window messages. It is the quick path: no long protocol, no extra analysis, no `opencode run`.

## Default Behavior

1. Send the user's intended message as raw text to the existing OpenCode chat window.
2. If no OpenCode chat exists, open `~/Desktop/OpenCode.app` to create/show it, then send.
3. Keep it short. Do not wrap simple messages in a coordination contract.
4. For complex planning, architecture review, or multi-file handoff, use the heavier `$opencode` collaboration skill instead.

## Bash Interface

Fast raw send:

```bash
/Users/poincare/.codex/skills/opencode-window/scripts/send.sh "message"
```

Pipe content:

```bash
printf '%s\n' "message" | /Users/poincare/.codex/skills/opencode-window/scripts/send.sh
```

Show the window only:

```bash
/Users/poincare/.codex/skills/opencode-window/scripts/attach.sh
```

Useful flags:

- `--no-enter` paste only, do not submit.
- `--no-focus` send without pulling the Terminal window forward.
- `--cwd PATH` working directory if OpenCode must be started.
- `--dry-run` resolve target without sending.

## Rule

Be quick and direct. Only pause to think when the content is genuinely complex or risky.
