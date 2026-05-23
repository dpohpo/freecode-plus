---
name: blackboard
description: File-based task board for multi-agent self-assignment. Agents read the blackboard, claim tasks, update status. Zero infrastructure.
user-invocable: "true"
triggers:
  - /blackboard
  - blackboard
  - task board
  - agent task
---

# Blackboard — Agent Self-Assignment Task Board

Distilled from [vibe-kanban](https://github.com/BloopAI/vibe-kanban) (24k stars) + [agent-kanban](https://github.com/saltbo/agent-kanban) (140 stars).

## Core Concept

Single JSON file = shared blackboard. Agents read it, claim tasks, update status. No DB, no server, no UI.

```
.blackboard/board.json  ← the blackboard (auto-created)
```

## CLI: `python3 ~/.claude/skills/blackboard/blackboard.py`

Alias: `bb="python3 ~/.claude/skills/blackboard/blackboard.py"`

### Quick Reference

```bash
BB="python3 ~/.claude/skills/blackboard/blackboard.py"

# Initialize board
$BB init

# Add tasks (lead creates)
$BB add "Implement auth module" -p high -l "backend,security"
$BB add "Write unit tests" --depends <task-id>
$BB add "Code review" --depends <task-id1>,<task-id2>

# Agent reads the board
$BB summary                    # Quick overview
$BB list                       # Full listing
$BB list --available           # Only claimable tasks (not blocked)
$BB next                       # Recommend next task (by priority)

# Agent claims & works
$BB claim <task-id> <agent-name>           # Claim a task
$BB update <task-id> start                 # Start working
$BB update <task-id> review --note "PR ready"  # Submit for review

# Lead/Critic reviews
$BB update <task-id> complete --note "LGTM"    # Approve
$BB update <task-id> reject --note "Fix X"     # Send back

# Utilities
$BB info <task-id>             # Task details + history
$BB log -t 10                  # Last 10 actions
$BB list -a lingbao            # Tasks owned by lingbao
```

## State Machine

```
todo ──claim──→ claimed ──start──→ in_progress ──review──→ in_review
  ↑                                    │                      │  │
  └────────────release─────────────────┘              complete│  │reject
                                                         ↓    │  ↓
                                                       done    in_progress

cancel: any active status → cancelled
release: claimed/in_progress → todo (frees task)
```

## Role Permissions

| Action   | agent | lead | critic |
|----------|-------|------|--------|
| claim    | yes   |      |        |
| start    | yes   |      |        |
| review   | yes   |      |        |
| complete |       | yes  | yes    |
| reject   |       | yes  | yes    |
| cancel   |       | yes  |        |
| release  | yes   | yes  |        |

## Agent Self-Assignment Protocol

When an agent (e.g., lingbao) needs work:

```
1. $BB summary              → Read board state
2. $BB next --agent lingbao → Get recommendation
3. $BB claim <id> lingbao   → Claim it (atomic, fails if already claimed)
4. $BB update <id> start    → Mark in_progress
5. ... do the work ...
6. $BB update <id> review   → Submit for review
```

## Dependencies (DAG)

Tasks can depend on other tasks. A task with unfinished deps is **BLOCKED** and cannot be claimed.

```bash
$BB add "Design API" -p high
# → [abc12345] Design API

$BB add "Implement API" --depends abc12345
# → [def67890] Implement API (blocked until abc12345 is done)
```

## Integration with 一气化三清

| God   | Role   | Board Operations |
|-------|--------|-----------------|
| Taiyi | Lead   | add, cancel, complete, reject, release |
| Yuanshi | Planner | add (creates tasks), summary |
| Lingbao | Executor | claim, start, review |
| Daode | Critic | complete, reject |
| Guanmiao | Observer | summary, list, log |

### Workflow

```
1. Taiyi/Yuanshi:  $BB add "task" -p high     → Create tasks
2. Lingbao:        $BB next && $BB claim       → Self-assign
3. Lingbao:        $BB update <id> start/review → Work & submit
4. Daode:          $BB list -s in_review        → Find reviews
5. Daode:          $BB update <id> complete/reject → Verdict
6. Guanmiao:       $BB summary && $BB log       → Report status
```

## Environment Variable

Override board location: `BLACKBOARD_FILE=path/to/board.json`
