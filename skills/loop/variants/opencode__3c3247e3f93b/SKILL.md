---
name: loop
description: Follow the local triad loopback protocol for Codex, OpenCode, and CCGLM/freeglm. Use when a message contains $loop, /loop, TRIAD_LOOPBACK_V1, or asks agents to report to the next agent until the task is closed.
---

# Loop

Use this skill for the 6.0b loopback workflow between Codex, OpenCode, and CCGLM/freeglm.

## Trigger Forms

- Messages to Codex use `$loop`.
- Messages to OpenCode or CCGLM/freeglm use `/loop`.
- `TRIAD_LOOPBACK_V1` also means this skill is active.

## Roles

- Codex = Planner, signs with `/codex`.
- OpenCode = Orchestrator, signs with `$opencode`.
- CCGLM/freeglm = Executor, signs with `$ccglm`.

The signature identifies the sender, not the recipient.

## Required Loop

Preferred one-command 6.0b start:

`bash /Volumes/金阳/brain/scripts/triad-6b.sh loop --cwd PATH "task"`

Equivalent shortcut:

`bash /Volumes/金阳/brain/scripts/triad-loop.sh --cwd PATH "task"`

Before a lower-level run, or whenever an agent window is missing/not visible, use:

`bash /Volumes/金阳/brain/scripts/triad-ensure-visible.sh --cwd PATH`

This ensures the visible interactive lanes for OpenCode and CCGLM/freeglm. Do not use Opus or `/yqhsq` in the default loop. Use the legacy Claude Code/yqhsq lane only when explicitly requested.

Normal route:

1. Codex Planner -> OpenCode Orchestrator:
   `bash /Volumes/金阳/brain/scripts/triad-planner-to-orchestrator.sh --run-id ID --cwd PATH "plan"`
2. OpenCode Orchestrator -> CCGLM Executor:
   `bash /Volumes/金阳/brain/scripts/opencode-to-glm.sh --run-id ID --cwd PATH "executor task"`
   - This is the preferred OpenCode-facing wrapper. It uses the stable direct iTerm/freeglm transport and submits pasted-text composers with a session-level Enter.
   - `triad-orchestrator-to-executor.sh` remains the lower-level route script.
3. CCGLM Executor -> OpenCode Orchestrator:
   `bash /Volumes/金阳/brain/scripts/triad-executor-to-orchestrator.sh --run-id ID --cwd PATH "delivery report"`
4. OpenCode Orchestrator -> Codex Planner:
   `bash /Volumes/金阳/brain/scripts/triad-orchestrator-to-planner.sh --run-id ID --cwd PATH "orchestration report"`

Each agent must report to the next responsible agent when its part is done. Do not stop at local completion unless the next report fails; if blocked, report the blocker through the same route.

## Window Visibility

- Agent coordination must happen through interactive chat windows, not one-shot CLI agent runs.
- OpenCode must use the OpenCode chat window for orchestration.
- CCGLM/freeglm defaults to direct iTerm2 session `ccglm-iterm`; tmux is only a legacy fallback through `CCGLM_TRANSPORT=tmux`.
- The OpenCode -> GLM wrapper submits pasted-text composers with an iTerm session-level Enter. If a pasted CCGLM message remains at a `[Pasted text ...]` composer prompt, rerun `bash /Volumes/金阳/brain/scripts/opencode-to-glm.sh ...` or submit normal `Enter`.

## Message Requirements

Every handoff must include:

- `$loop` for Codex, or `/loop` for OpenCode/CCGLM
- `TRIAD_LOOPBACK_V1`
- `run_id`
- route
- cwd
- sender and recipient
- task/result
- exact next script to run
- changed files/actions, verification, blockers, and next requested action

## Local Skill Copies

- Codex: `/Users/poincare/.codex/skills/loop/SKILL.md`
- Claude/Free Code/CCGLM: `/Users/poincare/.claude/skills/loop/SKILL.md`
- OpenCode reference copy: `/Users/poincare/.config/opencode/skills/loop/SKILL.md`

If an agent cannot load native skills, it must read one of these paths directly before acting.
