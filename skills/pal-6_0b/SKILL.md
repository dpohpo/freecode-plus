---
name: pal-6_0b
description: Use PAL MCP in the local 6.0B collaboration stack so fresh contexts do heavy work and the main agent keeps only conclusions, decisions, and next actions.
user-invocable: "true"
---

# PAL 6.0B

Use this skill when Claude Code should drive PAL MCP as part of the local 6.0B system.

## Core Intent

- PAL is for fresh-context heavy work, not for cluttering the current context.
- Heavy investigation, debate, or long code review should happen in PAL subflows.
- The current agent keeps only:
  - conclusions
  - evidence worth carrying forward
  - explicit next actions

## Role Contract Inside yqhsq

- `taiyi`
  - receives all top-level PAL tasks first
  - delegates; does not become the worker
- `yuanshi`
  - chooses PAL workflow shape
  - decides whether the task needs `planner`, `consensus`, `thinkdeep`, or `clink`
- `lingbao`
  - executes implementation tasks after PAL planning/review
- `daode`
  - uses PAL for final review / precommit style checks
- `guanmiao`
  - uses PAL for gap finding, missing evidence, and state observation
- `siguo`
  - records PAL, cc, browser, and MCP failures separately
- `xuanshu`
  - watches context health, 5-hour usage, Codex web health, and freshness recommendations

## 6.0B Rules

1. All important PAL requests must start from explicit sender / recipient / task framing.
2. If current context is above `40%`, do not assign heavy work to that agent.
3. Above `40%`, prefer one of:
   - PAL `clink` fresh CLI context
   - PAL `planner` / `consensus` offload
   - task handoff to a fresher yqhsq agent
   - `/clear` + context reinjection only when the task truly continues in-place
4. The answer returned from PAL must be compressed into:
   - decision
   - strongest evidence
   - concrete next step
5. Web lanes are part of the loop when PAL recommendations need external verification, cross-model critique, or browser-only workflows.

## Recommended Tool Choice

- Architecture / tool choice:
  - `consensus`
  - `planner`
- Root-cause investigation:
  - `debug`
  - `thinkdeep`
- Heavy external fresh-context work:
  - `clink`
- Final review before merge or handoff:
  - `codereview`
  - `precommit`
- API / SDK uncertainty:
  - `apilookup`

## Output Contract

Every PAL-assisted turn should end with:

```md
[PAL_DECISION]
[PAL_EVIDENCE]
[PAL_NEXT]
```

## Anti-Patterns

- Do not dump PAL raw transcripts back into the main context.
- Do not ask a >40% context agent to do the deepest investigation.
- Do not let `taiyi` absorb executor work.
- Do not treat PAL as a replacement for local verification, tests, or official docs.
