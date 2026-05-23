# Slash Alias Table

## Stable Aliases

- `/cc`
  - `cc-yqhsq-operator`
  - `bash /Volumes/金阳/brain/scripts/tmux-opus-yqhsq.sh`

- `/yqhsq`
  - `cc-yqhsq-operator`
  - `bash /Volumes/金阳/brain/scripts/tmux-opus-yqhsq.sh`

- `/browser`
  - `brain-web-operator`

- `/web`
  - `brain-web-operator`

- `/collab`
  - `agent-collab-catalog`

- `/memory`
  - `bash /Volumes/金阳/brain/scripts/brain-memory-status.sh`
  - `bash /Volumes/金阳/brain/scripts/brain-memory-context.sh --agent codex`
  - `bash /Volumes/金阳/brain/scripts/brain-memory-skill-index.sh`

## Notes

- Slash aliases are explicit routing inputs, not natural-language hints.
- For Codex, `/cc` means the full `cc + Opus + /yqhsq` bootstrap path.
- Prefer shell wrappers over extra prompt scaffolding when an alias already has
  a stable wrapper.
