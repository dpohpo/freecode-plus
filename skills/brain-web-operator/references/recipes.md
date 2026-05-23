# Browser MCP Recipes

## Tool Map

- `web_scan_tabs`
  - Use to discover current `page_id` values in the debug Chrome instance.
- `web_register_tab`
  - Use once per tab after a human has prepared and logged into the page.
- `web_focus_tab`
  - Use before any action that depends on the visible target page.
- `web_chat_send`
  - Use for one-shot message send.
- `web_chat_interrupt`
  - Use only when a page is already generating.
- `web_export_markdown`
  - Use for artifact or markdown extraction. Prefer this over browser downloads.
  - On Claude chat tabs, the default export path now targets the latest
    `standard-markdown` answer block instead of whole-page `innerText`.

## Fast Setup Recipe

1. Call `web_scan_tabs`.
2. Identify the correct `page_id` for each Claude/GPT tab.
3. Call `web_register_tab` for each page with a stable label and a short `purpose` / `topic`.
4. From then on, work only by label.

Recommended labels:

- `claude-arch`
- `claude-research`
- `claude-writing`
- `gpt-review`
- `gpt-ops`
- `gpt-brain`

## Standard Workspace Recipe

For the fixed four-tab browser workspace, prefer the shell entrypoints over raw
tool calls:

```bash
bash /Volumes/金阳/brain/scripts/agent-browser-up.sh
bash /Volumes/金阳/brain/scripts/agent-browser-status.sh
bash /Volumes/金阳/brain/scripts/agent-browser-restart.sh
```

Current fixed labels:

- `claude-login`
- `gpt-login`
- `gemini-login`
- `grok-login`

## Send Recipe

Use this shape when a tab is already registered:

```python
web_chat_send(
    label="gpt-review",
    message="Review PR #17 for regressions and missing tests.",
    wait_for_stop=True,
)
```

Use `interrupt_after_s` only when you intentionally want a bounded partial answer or an interrupt test.

## Interrupt Recipe

Use this only after confirming the page is generating or after a `web_chat_send` that started generation:

```python
web_chat_interrupt(
    label="claude-research",
    wait_for_stop=True,
)
```

If the result says `not_generating`, do not retry blindly. Re-check the page state first.

## Claude Model Switch Recipe

Use the dedicated shell wrapper instead of re-deriving the menu path:

```bash
bash /Volumes/金阳/brain/scripts/claude-web-model-set.sh opus claude-login
```

Supported aliases include:

- `opus`
- `opus-4.6`
- `opus-4.5`
- `opus-3`
- `sonnet`
- `sonnet-4.5`
- `haiku`

Important behavior:

- In the current Claude web UI, switching model may move to a fresh `Untitled`
  chat.
- Treat model switching as a separate action from message send.
- Re-check page state after switching before sending the next prompt.

## Claude Multi-Chat Label Recipe

Use stable system labels for repeatable Claude chat lanes:

```bash
bash /Volumes/金阳/brain/scripts/claude-web-new-chat.sh claude-lab-a chat prompt-lab-a
bash /Volumes/金阳/brain/scripts/claude-web-new-chat.sh claude-lab-b chat prompt-lab-b
```

If you need to rename one of those system labels later:

```bash
bash /Volumes/金阳/brain/scripts/claude-web-relabel.sh claude-lab-a claude-prompt-lab
```

To bounce between two Claude chat lanes three times:

```bash
bash /Volumes/金阳/brain/scripts/claude-web-switch-loop.sh claude-lab-a claude-lab-b 3 0.2
```

For high signal-to-noise task isolation, prefer one labeled chat per task:

```bash
bash /Volumes/金阳/brain/scripts/claude-web-new-task-chat.sh claude-phase2 "Phase 2 retrieval redesign"
bash /Volumes/金阳/brain/scripts/claude-web-new-task-chat.sh claude-review "Security review"
bash /Volumes/金阳/brain/scripts/claude-web-switch-loop.sh claude-phase2 claude-review 3 0.2
```

Or use the one-shot pair wrapper:

```bash
bash /Volumes/金阳/brain/scripts/claude-web-task-pair.sh claude-phase2 "Phase 2 retrieval redesign" claude-review "Security review" 3 0.2
```

Rules:

- Treat these labels as system routing labels, not Claude's visible left-sidebar
  chat title.
- For specific-task work, use the first seeded task prompt to drive Claude's
  visible chat title instead of depending on the current rename UI.
- Registry writes are serialized operations. Do not rename two labels in
  parallel.

## Artifact Export Recipe

For Claude artifacts, prefer all of these together:

```python
web_export_markdown(
    label="claude-arch",
    artifact_title="Phase2 implementation",
    start_marker="Phase 2: 智能层",
    end_marker="Share",
    open_code_view=True,
    output_path="/Users/poincare/Desktop/phase2_claude.md",
)
```

Guidelines:

- Use `artifact_title` when the page contains a visible artifact card.
- Keep `open_code_view=True` for Claude artifacts.
- Set `start_marker` to the first heading of the real document, not the chat summary.
- Keep `end_marker="Share"` unless the page layout changes.

## Failure Patterns

- Exported file is suspiciously short:
  - You probably exported the summary, not the artifact body.
  - Re-run with `artifact_title` and `open_code_view=True`.

- Tab cannot be found by label:
  - Re-run `web_scan_tabs`.
  - The page may have been closed or reopened with a new `page_id`.
  - Re-register it.

- Send reports no input target:
  - The page is likely logged out, not fully loaded, or not a real chat page.

- Wrong tab was used:
  - Do not route by URL/title after registration.
  - Use `web_focus_tab` and then act by label.
