# Local Collaboration Stack

## Main Roles

- `Brain`:
  - reliable shared memory
  - long-term tracking
  - skill index
  - fresh-agent context generation
- `6.0B`:
  - fast shell-first wrappers
  - direct low-latency actions
- `cc`:
  - Claude Code runtime inside iTerm2/tmux
- `/yqhsq`:
  - multi-pane team bootstrap inside Claude Code

## Important Paths

- Brain repo: `/Volumes/金阳/brain`
- Shell wrappers: `/Volumes/金阳/brain/scripts`
- Shared memory root: `~/.brain/shared_memory`
- Fresh agent context: `~/.brain/shared_memory/injections/fresh-agent-context.md`
- Codex skills: `~/.codex/skills`

## Common Wrapper Commands

- `bash /Volumes/金阳/brain/scripts/tmux-opus-yqhsq.sh`
- `bash /Volumes/金阳/brain/scripts/web-chat-send.sh <label> "<message>"`
- `bash /Volumes/金阳/brain/scripts/web-chat-stop.sh <label>`
- `bash /Volumes/金阳/brain/scripts/web-chat-export.sh <label>`
- `bash /Volumes/金阳/brain/scripts/brain-memory-skill-index.sh`
- `bash /Volumes/金阳/brain/scripts/brain-memory-context.sh --agent codex`

## Common Task Combinations

- Ask a browser Claude tab to write a document:
  - `brain-web-operator`
- Wake `cc`, start `yqhsq`, then hand off work:
  - `cc-yqhsq-operator`
- Rebuild fresh context for a new Codex session:
  - `agent-collab-catalog`
  - then Brain memory wrappers

## Principle

Always prefer the narrowest reliable surface:

1. shell wrapper
2. dedicated MCP/browser tool
3. terminal automation
4. generic GUI control
