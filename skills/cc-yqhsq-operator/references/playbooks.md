# CC / YQHSQ Playbooks

## Main Wrapper

```bash
bash /Volumes/金阳/brain/scripts/tmux-opus-yqhsq.sh
```

This wrapper calls:

```bash
uv run brain-gui-cc --bootstrap-yqhsq
```

## Useful Overrides

```bash
cd /Volumes/金阳/brain
uv run brain-gui-cc --bootstrap-yqhsq --tmux-confirm yes
uv run brain-gui-cc --bootstrap-yqhsq --model-confirm yes
uv run brain-gui-cc --bootstrap-yqhsq --skill-confirm yes
```

## Healthy Markers

- `Claude Code v`
- `Opus 4`
- `模型已切换为 Opus`
- `一气化三清`
- `阵列完整，随时听令`
- tmux pane count `>= 5`

## Typical Failure Modes

- tmux asks a `yes/no` confirmation and the flow stalls
- Opus switch completes but yqhsq was never started
- yqhsq was already active in another tmux session

## What Not To Do

- Do not fall back to random GUI clicking if the wrapper can be retried with confirmation overrides.
- Do not treat partial terminal output as success if `yqhsq_started` is still false.
