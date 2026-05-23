---
name: ccglm
description: Send text to the main CCGLM/freeglm executor pane. Use when the user writes $ccglm, wants the old $cc main-agent workflow but started with freeglm, or wants triad executor routing without yqhsq/teamagent.
---

# CCGLM

`$ccglm` is `$cc` with two changes:

- startup command is `freeglm`
- yqhsq/teamagent is removed

Use it as the GLM executor lane in the Codex/OpenCode loopback workflow.

## Primary Interface

Compiled send, same role as `$cct`:

```bash
bash /Volumes/金阳/brain/scripts/ccglm.sh "message"
bash /Volumes/金阳/brain/scripts/ccglm-send-compiled.sh "message"
```

Raw send, same role as `cc-main-send.sh`:

```bash
bash /Volumes/金阳/brain/scripts/ccglm-main-send.sh "literal text"
```

Scripted 6.0b lane bootstrap:

```bash
bash /Volumes/金阳/brain/scripts/ccglm-6b.sh amazon-selection --cwd PATH
bash /Volumes/金阳/brain/scripts/ccglm-lanes.sh --cwd PATH --task "task" \
  --lane "orchestrator:小o:role text" \
  --lane "executor:小e:role text"
```

6.0b triad verification:

```bash
bash /Volumes/金阳/brain/scripts/triad-6b.sh verify --cwd PATH
bash /Volumes/金阳/brain/scripts/ccglm-6b.sh verify
```

## Behavior

- Default transport is direct iTerm2, not tmux.
- Reuse an iTerm session named `ccglm-iterm` when present.
- If missing, open iTerm2, `cd` to the requested cwd, type `freeglm`, press Enter, wait, then inject the message and press Enter.
- For multiple freeglm windows, use `ccglm-6b.sh start-lanes` or `ccglm-lanes.sh`; it starts lanes sequentially, gives each lane a stable session name and short name, sends a `CCGLM_LANE_BOOTSTRAP_V1` contract, and verifies distinct ttys.
- The iTerm sender serializes all iTerm automation with a lock, so simultaneous callers do not race on `current window` or inject into the wrong lane.
- OpenCode handoffs should call `bash /Volumes/金阳/brain/scripts/opencode-to-glm.sh ...`; that wrapper keeps the stable iTerm/freeglm submit behavior in one place.
- The legacy tmux transport is available only by setting `CCGLM_TRANSPORT=tmux`.
- If the first non-space character is `/`, send raw so slash commands keep working.
- Sender signature for reports is `$ccglm`.

## Rules

- Do not use yqhsq.
- Do not use teamagent.
- Do not inspect, print, or expand the user's `freeglm` alias/function.
- Preserve the existing single-lane behavior of `ccglm.sh` and `ccglm-main-send.sh`; use the 6.0b lane bootstrap only when multiple named windows are requested.
- For triad handoff, `triad-orchestrator-to-executor.sh` routes here.
