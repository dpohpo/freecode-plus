---
name: cc-yqhsq-operator
description: Bootstrap, recover, and verify Claude Code in iTerm2/tmux with `Opus` and `/yqhsq`. Use when Codex needs to open `cc`, reuse or enter `tmux`, switch to Opus, start the yqhsq team, or handle `yes/no` terminal confirmations during that bootstrap flow.
---

# CC YQHSQ Operator

Use this skill for the `cc` terminal lane. The preferred path is the existing wrapper, not ad-hoc typing.

## Quick Start

Run:

```bash
bash /Volumes/金阳/brain/scripts/tmux-opus-yqhsq.sh
```

For weak agents that should not guess between main `cc` and `yqhsq`, prefer:

```bash
bash /Volumes/金阳/brain/scripts/cc-safe-send.sh guide
```

If you need explicit stage control, run:

```bash
cd /Volumes/金阳/brain
uv run brain-gui-cc --bootstrap-yqhsq
```

## Confirmation Handling

The bootstrap flow supports stage-specific confirmation overrides:

```bash
uv run brain-gui-cc --bootstrap-yqhsq --tmux-confirm yes
uv run brain-gui-cc --bootstrap-yqhsq --model-confirm yes
uv run brain-gui-cc --bootstrap-yqhsq --skill-confirm yes
```

Rules:

- Default `auto` answers `yes` for non-destructive prompts.
- Default `auto` answers `no` for overwrite/delete/terminate style prompts.
- Use explicit `yes` when tmux or Claude surfaces a harmless `yes/no` gate that blocks progress.

## Success Criteria

Treat the bootstrap as successful only when the result shows:

- `tmux_started = true`
- `opus_ready = true`
- `yqhsq_started = true`

The terminal runner also reports pane count. A healthy yqhsq state now reaches `team_panes >= 7`.

## Recovery

If the first run stalls:

1. Re-run the wrapper once.
2. If notes mention a confirmation gate, re-run with the relevant `--*-confirm yes`.
3. If tmux already exists, do not invent a second manual flow unless the wrapper keeps failing.

## Coordination Rules

- Use this skill only for the `cc` terminal lane.
- Use `brain-web-operator` for browser chat tabs.
- Keep long-term memory in `Brain`, not inside the transient terminal session.

## Reference

- Load `references/playbooks.md` for exact commands, expected markers, and common failure patterns.
