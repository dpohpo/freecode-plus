# Agent Dialogue Recipes

## Build Only

```bash
bash /Volumes/金阳/brain/scripts/agent-dialogue-build.sh \
  --self-agent codex \
  --target-agent claude \
  --task "Review the 6.0B MCP design" \
  --magic auto
```

## Send to Claude Web

```bash
bash /Volumes/金阳/brain/scripts/claude-web-new-task-chat.sh claude-phase2 "Phase 2 retrieval redesign"

bash /Volumes/金阳/brain/scripts/agent-dialogue-send.sh \
  --self-agent codex \
  --target-agent claude \
  --label claude-phase2 \
  --task "Review the 6.0B MCP design" \
  --context-file /Volumes/金阳/brain/docs/prompts/agent_dialogue_6_0b_context.md \
  --magic always
```

## Send to GPT Web

```bash
bash /Volumes/金阳/brain/scripts/web-new-task-chat.sh gpt-web gpt-phase2 "Phase 2 retrieval redesign"

bash /Volumes/金阳/brain/scripts/agent-dialogue-send.sh \
  --self-agent codex \
  --target-agent gpt \
  --label gpt-phase2 \
  --task "Review the 6.0B MCP design" \
  --context-file /Volumes/金阳/brain/docs/prompts/agent_dialogue_6_0b_context.md \
  --magic always
```

## Send to cc / yqhsq

```bash
bash /Volumes/金阳/brain/scripts/agent-dialogue-send.sh \
  --self-agent codex \
  --target-agent cc \
  --task "Review the 6.0B MCP design" \
  --magic always
```

## Send Compiled Prompt To Main cc

```bash
bash /Volumes/金阳/brain/scripts/cc-main-send-compiled.sh \
  "Review the 6.0B MCP design"
```

Legacy alias:

```bash
bash /Volumes/金阳/brain/scripts/cct.sh \
  "Review the 6.0B MCP design"
```

## Notes

- Use `--magic auto` for heuristic routing, `--magic always` for forced deep analysis.
- For exact literal text in the main `cc` pane, bypass the compiler and use:
  - `bash /Volumes/金阳/brain/scripts/cc-main-send.sh "message"`
- For repeatable work, keep a stable task label and send multiple compiled prompts
  into the same lane instead of opening one-off chats.
- The builder is the source of truth for sender/recipient framing. Do not
  restate that contract manually unless you are debugging the builder itself.
