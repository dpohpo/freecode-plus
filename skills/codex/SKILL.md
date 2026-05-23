---
name: codex
description: 反向控制网页 Codex / Codex app / Codex CLI — 编译 6.0B prompt 后优先注入 Codex web，支持 slash passthrough 和 raw 模式
user-invocable: "true"
---

# /codex — Claude Code → 网页 Codex 反向控制链路

> 从 Claude Code 侧向 Codex 发送任务。默认编译 6.0B Agent Dialogue prompt，并优先走 `codex-login` 网页通道；slash 命令直通，无需手工 UI。

## 触发条件

当用户输入 `/codex <message>` 时触发。

## 快速使用

```
/codex 重构 auth 模块，拆分 token 管理到独立文件
/codex --raw 直接发送原文，不编译
/codex --desktop 用桌面 app 注入而非网页通道
/codex --cli 用 CLI 模式而非网页通道
/codex /help                     ← slash 命令直通 Codex
```

## 工作流程

```
用户输入 /codex <message>
        │
        ├── message 以 "/" 开头？
        │     └── YES → slash passthrough → codex-send.sh 原样注入
        │
        ├── --raw 标志？
        │     └── YES → 跳过编译 → codex-send.sh 原样注入
        │
        └── NO → 6.0B Prompt 编译
              │
              ├── agent-dialogue-build.sh
              │     --self-agent cc-main
              │     --target-agent codex
              │     --task "<message>"
              │     --magic always (默认)
              │
              └── codex-send.sh 注入编译后 prompt
                    ├── --web (默认): Brain GUI 注入 `codex-login`
                    ├── --desktop: AppleScript 注入运行中的 Codex app
                    └── --cli: codex exec 非交互执行
```

## 执行指令

收到 `/codex` 调用后，执行以下步骤：

### Step 1: 解析参数

从用户输入中提取：
- `message`: 要发送给 Codex 的内容（必需）
- `--raw`: 是否跳过 6.0B 编译（可选，默认 false）
- `--desktop`: 是否改走桌面 app 注入（可选，默认 false）
- `--cli`: 是否用 CLI 模式（可选，默认 desktop）
- `--magic auto|always|never`: magic block 策略（可选，默认 always）
- `--timeout N`: 超时秒数（可选，默认 120）

### Step 2: 检查 Codex 可用性

```bash
# Web 模式：检查并使用 `codex-login` 标签到网页 Codex
python3 - <<'PY'
import json
from pathlib import Path
registry = json.loads((Path.home()/".brain"/"gui_tab_registry.json").read_text())
print("codex-login" in registry)
PY

# Desktop 模式：检查 Codex app 是否运行
pgrep -q -f "Codex.app/Contents/MacOS/Codex" && echo "Codex running" || echo "Codex not running"

# CLI 模式：检查 codex CLI 是否存在
test -x /Applications/Codex.app/Contents/Resources/codex && echo "CLI ok" || echo "CLI missing"
```

如果不可用，报告错误并建议用户启动 Codex。

### Step 3: 执行发送

```bash
# 标准模式（6.0B 编译 + web 注入）
bash /Volumes/金阳/brain/scripts/codex.sh "<message>"

# Raw 模式
bash /Volumes/金阳/brain/scripts/codex.sh --raw "<message>"

# Desktop 模式
bash /Volumes/金阳/brain/scripts/codex.sh --desktop "<message>"

# CLI 模式
bash /Volumes/金阳/brain/scripts/codex.sh --cli "<message>"

# Slash passthrough（自动检测）
bash /Volumes/金阳/brain/scripts/codex.sh "/some-codex-command"
```

### Step 4: 报告结果

向用户报告注入结果的 JSON（mode, prompt_length, injected 状态）。

## 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| message | string | 必需 | 发送给 Codex 的任务或命令 |
| --raw | flag | false | 跳过 6.0B prompt 编译，原文发送 |
| --desktop | flag | false | 使用 Codex 桌面 app 而非网页通道 |
| --cli | flag | false | 使用 codex CLI 而非网页通道 |
| --magic | auto/always/never | always | 6.0B magic block 策略 |
| --timeout | int | 120 | 发送超时秒数 |

## 底层脚本

| 脚本 | 路径 | 职责 |
|------|------|------|
| codex.sh | /Volumes/金阳/brain/scripts/codex.sh | 高层入口：编译 + 分发 |
| codex-send.sh | /Volumes/金阳/brain/scripts/codex-send.sh | 低层传输：web/desktop/CLI 注入 |
| agent-dialogue-build.sh | /Volumes/金阳/brain/scripts/agent-dialogue-build.sh | 6.0B prompt 编译器 |

## 依赖

- `codex-login` 网页通道可用（web 模式）或 Codex desktop app 运行中（desktop 模式）或 CLI 可执行（CLI 模式）
- brain_mcp agent_dialogue 模块（prompt 编译）
- macOS（AppleScript desktop 注入）

## 与 agent_dialogue 的关系

`/codex` 是 agent_dialogue 6.0B 系统的反向通道：

- agent_dialogue 支持 `codex` 作为 target_agent（已注册路由）
- `codex.sh` 调用 `agent-dialogue-build.sh` 编译 prompt
- prompt 编译后通过 `codex-send.sh` 注入

这形成了 **CC ↔ Codex Web 双向同构链路**。
