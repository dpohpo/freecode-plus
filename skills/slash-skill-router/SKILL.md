---
name: slash-skill-router
description: Route leading slash aliases like `/cc`, `/browser`, `/collab`, and `/memory` to the correct local skill or shell wrapper before semantic reasoning. Use when a prompt begins with `/...` or when Codex should treat slash commands as explicit local capability selectors instead of free-form prose.
---

# Slash Skill Router

Use this skill whenever the user starts a request with `/alias` or clearly wants
Codex to treat slash commands as stable local skill triggers.

## Rule

- Treat a leading `/alias` token as explicit routing input.
- Resolve the alias before free-form semantic interpretation.
- Prefer an existing shell wrapper when the alias maps to a repeatable action.
- If an alias maps to a skill, load the smallest relevant skill and then call
  the wrapper or MCP surface named in that skill.

## Built-In Alias Map

- `/cc`
  - Meaning: bootstrap Claude Code in iTerm2/tmux, switch to Opus, and enter
    `/yqhsq`.
  - Primary path:
    - `cc-yqhsq-operator`
    - `bash /Volumes/金阳/brain/scripts/tmux-opus-yqhsq.sh`

- `/yqhsq`
  - Meaning: ensure the current Claude Code collaboration team is running.
  - Primary path:
    - `cc-yqhsq-operator`
    - `bash /Volumes/金阳/brain/scripts/tmux-opus-yqhsq.sh`

- `/browser`
  - Meaning: route browser chat work by stable tab label.
  - Primary path:
    - `brain-web-operator`

- `/web`
  - Meaning: same routing intent as `/browser` unless a narrower local alias is
    later defined.
  - Primary path:
    - `brain-web-operator`

- `/collab`
  - Meaning: discover the local multi-agent collaboration stack first.
  - Primary path:
    - `agent-collab-catalog`

- `/memory`
  - Meaning: use Brain shared memory as the source of truth.
  - Primary path:
    - `bash /Volumes/金阳/brain/scripts/brain-memory-status.sh`
    - `bash /Volumes/金阳/brain/scripts/brain-memory-context.sh --agent codex`
    - `bash /Volumes/金阳/brain/scripts/brain-memory-skill-index.sh`

## Unknown Alias Handling

- Search the local skill index for a matching skill name or obvious alias.
- Search collaboration references before asking the user.
- If no route exists, say the alias is unknown and continue with the smallest
  safe fallback.

## Reference

- Read [aliases.md](references/aliases.md) for the compact alias table and
  routing notes.
