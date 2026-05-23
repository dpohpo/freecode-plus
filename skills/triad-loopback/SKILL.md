---
name: triad-loopback
description: Coordinate Codex, OpenCode, and CCGLM/freeglm as a scripted 6.0b triad with loopback reports. Use when the user wants Codex as planner, OpenCode as orchestrator, and a local GLM executor, or asks for agent-to-agent loopback until a task is complete.
---

# Triad Loopback

Use this skill for three-agent work where Codex plans, OpenCode orchestrates, and CCGLM executes through the local `freeglm` lane.

## Roles And Signatures

- Codex = Planner, signs messages with `/codex`.
- OpenCode = Orchestrator, signs messages with `$opencode`.
- CCGLM = Executor, signs messages with `$ccglm`.

The tag is the sender identity signature, not the recipient command.

## Loopback Contract

Every handoff must include:

- `$loop` when the recipient is Codex, or `/loop` when the recipient is OpenCode/CCGLM
- `run_id`
- sender and recipient
- current route
- task or result
- required next report path
- exact script the next agent should call when done

Normal task loop:

1. Codex plans and sends to OpenCode:
   `triad-6b.sh loop "task"`, `triad-start.sh "task"`, or `triad-planner-to-orchestrator.sh`.
2. OpenCode decomposes/assigns and sends to CCGLM:
   `opencode-to-glm.sh --run-id ID "executor task"`.
3. CCGLM executes and reports to OpenCode:
   `triad-executor-to-orchestrator.sh --run-id ID "delivery summary"`.
4. OpenCode verifies/routes result and reports to Codex:
   `triad-orchestrator-to-planner.sh --run-id ID "orchestration summary"`.
5. Codex closes or sends another plan step to OpenCode.

Do not stop mid-loop unless blocked; report the blocker to the next responsible agent.

## Bash Interface

Preferred 6.0b entrypoint:

```bash
bash /Volumes/金阳/brain/scripts/triad-6b.sh loop --cwd PATH "task"
bash /Volumes/金阳/brain/scripts/triad-6b.sh verify --cwd PATH
bash /Volumes/金阳/brain/scripts/triad-6b.sh status
```

Convenience alias:

```bash
bash /Volumes/金阳/brain/scripts/triad-loop.sh --cwd PATH "task"
```

Start a triad run:

```bash
/Users/poincare/.codex/skills/triad-loopback/scripts/triad-start.sh "task"
```

Route-specific sends:

```bash
/Users/poincare/.codex/skills/triad-loopback/scripts/triad-planner-to-orchestrator.sh --run-id ID "plan"
/Users/poincare/.codex/skills/triad-loopback/scripts/opencode-to-glm.sh --run-id ID "task"
/Users/poincare/.codex/skills/triad-loopback/scripts/triad-executor-to-orchestrator.sh --run-id ID "result"
/Users/poincare/.codex/skills/triad-loopback/scripts/triad-orchestrator-to-planner.sh --run-id ID "summary"
```

Status:

```bash
/Users/poincare/.codex/skills/triad-loopback/scripts/triad-status.sh
```

## Rules

- Use raw chat-window delivery. Do not call model CLI one-shot commands.
- Include the `loop` skill trigger and skill paths in every handoff.
- Use `$ccglm`/`freeglm` for executor routing; do not depend on yqhsq/teamagent.
- Keep simple messages short; use detailed payloads only for complex work.
- Prefer `--no-focus` for background reporting and default focus for user-facing starts.
- If you are Codex and you send a triad handoff, your user-facing reply starts with `/codex`.
