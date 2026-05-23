# Browser MCP Recipes

## Register Existing Logged-In Tabs

Use when the human already opened the browser pages and you should bind stable labels:

1. `web_scan_tabs`
2. Match each tab by current page content
3. `web_register_tab`
4. From then on, operate only by `label`

## Send A Message

1. `web_focus_tab`
2. `web_chat_send`
3. Default to `wait_for_stop=true`

## Interrupt A Long Response

1. `web_focus_tab`
2. Confirm the page is generating
3. `web_chat_interrupt`
4. Wait for stop before any next send

## Export A Claude Artifact

Use `web_export_markdown` with artifact-aware parameters.
For long markdown artifacts, prefer:

- `artifact_title`
- `start_marker`
- `end_marker="Share"`
- `open_code_view=true`

## Recovery Loop

If the action fails:

1. Re-run `web_scan_tabs`
2. Re-check the target page
3. Re-register if labels drifted
4. Retry the smallest necessary action
