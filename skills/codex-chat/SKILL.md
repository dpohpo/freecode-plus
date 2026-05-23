---
name: codex-chat
description: 与 Codex 桌面应用对话 — 自动激活 Codex 窗口，粘贴消息并发送。触发场景：(1) 用户说 "codex" 或 "跟 codex 说" (2) 用户要向 Codex 发消息 (3) 用户要跟 Codex 对话 (4) /codex <message> (5) 任何涉及与 Codex 交互的请求
version: 1.0.0
author: Poincare
---

# Codex Chat Skill

向 Codex 桌面应用发送消息并自动回车。

## 前置条件

- macOS
- Codex.app 已安装并运行 (`/Applications/Codex.app`)
- 已授予辅助功能权限 (System Settings → Privacy & Security → Accessibility)

## 使用方式

### 方式一：直接发送消息

用户说"跟 Codex 说你好"或"/codex 你好"，执行：

```bash
echo "<MESSAGE>" | pbcopy && osascript -e '
tell application "Codex" to activate
delay 0.5
tell application "System Events"
    tell process "Codex"
        keystroke "v" using command down
        delay 0.3
        keystroke return
    end tell
end tell
'
```

### 方式二：仅输入不发送

用户说"在 Codex 输入 XXX"（不自动回车），去掉 `keystroke return` 行：

```bash
echo "<MESSAGE>" | pbcopy && osascript -e '
tell application "Codex" to activate
delay 0.5
tell application "System Events"
    tell process "Codex"
        keystroke "v" using command down
    end tell
end tell
'
```

### 方式三：发送多行消息

```bash
printf "<LINE1>\n<LINE2>" | pbcopy && osascript -e '
tell application "Codex" to activate
delay 0.5
tell application "System Events"
    tell process "Codex"
        keystroke "v" using command down
        delay 0.3
        keystroke return
    end tell
end tell
'
```

## 执行协议

1. 提取用户要发送的消息内容
2. 检查 Codex 是否在运行：`pgrep -x Codex > /dev/null`
3. 如果未运行，提示用户先启动 Codex
4. 将消息写入剪贴板（`echo "msg" | pbcopy`）
5. 激活 Codex 窗口
6. 粘贴（Cmd+V）
7. 按回车发送
8. 通知用户"已发送"

## 安全提醒

- 发送前确认消息内容，避免误操作
- 恢复剪贴板内容（可选）：发送前保存 `pbpaste`，发送后恢复
- 对于敏感命令，先仅输入不发送，让用户确认后再回车

## 故障排除

- **AppleScript 报错 "not allowed"**：需要在 System Settings → Privacy & Security → Accessibility 中添加终端/Claude 到允许列表
- **中文输入乱码**：使用剪贴板粘贴而非 `keystroke`，`keystroke` 不支持 CJK
- **Codex 未响应**：检查 Codex 是否在前台，增加 `delay` 到 1 秒
