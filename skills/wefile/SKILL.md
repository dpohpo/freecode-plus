---
name: wefile
description: Send local files to the user's WeChat File Transfer chat through macOS GUI automation. Use when the user writes `$wefile`, asks Codex to send/transfer/share a file through WeChat, says to send a file to "File Transfer", "文件传输助手", or "file management", or wants a built APK/document/archive delivered to their phone via WeChat.
---

# WeChat File Transfer

Use the bundled script for deterministic file delivery:

```bash
bash /Users/poincare/.codex/skills/wefile/scripts/wefile-send.sh /absolute/path/to/file
```

Convenience wrapper:

```bash
bash /Users/poincare/bin/wefile /absolute/path/to/file
bash /Users/poincare/bin/wefile-send /absolute/path/to/file
```

## Workflow

1. Verify the file exists before sending.
2. Run the script with an absolute path.
3. Prefer the default recipient `File Transfer`. If the user's WeChat UI is Chinese and search fails, retry with `--recipient 文件传输助手`.
4. If WeChat is already focused on the correct chat, retry with `--skip-search`.
5. Report whether the command completed. If it fails, include the script error and likely permission issue.

## Script Behavior

- Opens WeChat if needed.
- Searches for the recipient unless `--skip-search` is provided.
- Uses the bottom file button and macOS file picker to choose the file.
- Does not take screenshots.
- Overwrites the clipboard while running.

## Preconditions

- WeChat must be installed at `/Applications/WeChat.app` and logged in.
- `cliclick` must be installed; on this machine it is available at `/opt/homebrew/bin/cliclick`.
- macOS Accessibility permission must allow the active terminal/runtime to control WeChat.

## Examples

Send the latest daily schedule APK:

```bash
bash /Users/poincare/bin/wefile /Users/poincare/Desktop/DailySchedule.apk
```

Retry against a Chinese WeChat recipient name:

```bash
bash /Users/poincare/bin/wefile-send --recipient 文件传输助手 /Users/poincare/Desktop/DailySchedule.apk
```
