# Claude Code Hooks Reference

All 14 lifecycle hook events. Per project policy: configure ALL of them.
"可以不用但不能没有" — You may not need them all today, but they must all exist.

## Hook Events

| # | Event | Trigger | Use Case |
|---|-------|---------|----------|
| 1 | `SessionStart` (startup) | New session begins | Initialize event store, load CLAUDE.md, set context |
| 2 | `SessionStart` (resume) | Resume existing session | Restore state, replay recent events |
| 3 | `SessionStart` (compact) | After context compaction | Capture pre-compaction summary, verify critical state survived |
| 4 | `SessionStart` (clear) | After conversation clear | Reset working state, preserve persistent memory |
| 5 | `PreToolUse` | Before any tool call | Log intent, validate parameters, rate-limit expensive calls |
| 6 | `PostToolUse` | After tool call completes | Capture results to event store, detect truncation |
| 7 | `PreCompact` | Before context compaction | Last chance to save critical context to files |
| 8 | `Stop` | Agent thinks it's done | Run harness checks, self-prompt for continuation (ralph-wiggum) |
| 9 | `UserPromptSubmit` | User presses Enter | Log user intent, route to appropriate agent |
| 10 | `Notification` (permission) | Needs user approval | Log permission request, auto-approve if configured |
| 11 | `Notification` (idle) | Waiting for user input | Trigger idle tasks (memory GC, trace decay) |
| 12 | `SubagentStart` | Subagent spawned | Register in TEAM_STATE, assign task tracking |
| 13 | `SubagentStop` | Subagent finished | Capture results, update TEAM_STATE, trigger Critic |
| 14 | `TeammateMessage` | Message from teammate | Route to semantic channel, update blackboard |

## Hook Configuration (.claude/hooks.json)

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "python3 .claude/hooks/on_session_start.py \"$EVENT_TYPE\"",
        "description": "Initialize event store and load state"
      }
    ],
    "PreToolUse": [
      {
        "type": "command",
        "command": "python3 .claude/hooks/on_pre_tool.py \"$TOOL_NAME\" \"$TOOL_INPUT\"",
        "description": "Log tool intent to event store"
      }
    ],
    "PostToolUse": [
      {
        "type": "command",
        "command": "python3 .claude/hooks/on_post_tool.py \"$TOOL_NAME\" \"$TOOL_OUTPUT\"",
        "description": "Capture results, detect truncation"
      }
    ],
    "PreCompact": [
      {
        "type": "command",
        "command": "python3 .claude/hooks/on_pre_compact.py",
        "description": "Save critical context before compaction"
      }
    ],
    "Stop": [
      {
        "type": "command",
        "command": "python3 .claude/hooks/on_stop.py",
        "description": "Run harness telemetry, optionally self-prompt"
      }
    ],
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": "python3 .claude/hooks/on_user_prompt.py \"$PROMPT\"",
        "description": "Log user intent"
      }
    ],
    "SubagentStart": [
      {
        "type": "command",
        "command": "python3 .claude/hooks/on_subagent_start.py \"$AGENT_NAME\"",
        "description": "Register subagent in TEAM_STATE"
      }
    ],
    "SubagentStop": [
      {
        "type": "command",
        "command": "python3 .claude/hooks/on_subagent_stop.py \"$AGENT_NAME\" \"$EXIT_CODE\"",
        "description": "Capture results, trigger Critic if configured"
      }
    ],
    "TeammateMessage": [
      {
        "type": "command",
        "command": "python3 .claude/hooks/on_teammate_msg.py \"$FROM\" \"$MESSAGE\"",
        "description": "Route to semantic channel"
      }
    ]
  }
}
```

## Hook Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Continue normally |
| 1 | Log warning, continue |
| 2 | Block the action and feed stderr back to model as feedback |

**Project policy:** Exit code 2 is used only for harness telemetry feedback, never for capability restriction.

## Integration with Event Store

Every hook should append to the event store:

```python
import json, datetime, pathlib

def emit(event_type: str, payload: dict, store_path: str = ".immortal-agent/events.jsonl"):
    event = {
        "type": event_type,
        "timestamp": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(timespec="seconds"),
        "payload": payload,
    }
    with open(store_path, "a") as f:
        f.write(json.dumps(event) + "\n")
```
