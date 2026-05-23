---
name: codex-coord
version: 2.0.0
description: OpenCode-Codex 双向协作协议。标签标识发送方身份，左脚踩右脚闭环。
triggers:
  - /codex
  - "$opencode"
  - "跟codex说"
  - "让codex"
  - "codex协作"
---

# OpenCode ↔ Codex 双向协作协议 v2

## 核心规则 — 标签 = 发送方身份

1. **OpenCode 发给 Codex 的消息必须以 `$opencode` 开头** — 告诉 Codex "这是 OpenCode 说的"
2. **Codex 发给 OpenCode 的消息必须以 `/codex` 开头** — 告诉 OpenCode "这是 Codex 说的"
3. 标签是**发送方签名**，不是收件人地址
4. 每次通信必须 **全量共享**：上下文、已完成、待办、决策
5. 任务不完不停止，回复必有标签

## 左脚踩右脚闭环

```
┌──────────┐  $opencode（我是OpenCode）  ┌──────────┐
│ OpenCode │ ────────────────────────────→ │  Codex   │
│          │                               │          │
│          │ ←──────────────────────────── │          │
└──────────┘  /codex（我是Codex）          └──────────┘
     ↑                                          │
     └──────── 验证→推进→再发 $opencode ─────────┘
```

## 消息格式

### OpenCode → Codex

```
$opencode

## 📤 OpenCode → Codex

### 项目信息
- Root: <path>
- Stage: <P0/P1/P2/P3>

### 已完成 ✅
- [x] <item>

### 需要你做 📋
- [ ] <task>

### 关键决策 📌
- <decision>

回复必须带 /codex。任务做不完不能停。
```

### Codex → OpenCode（期望格式）

```
/codex

## 📥 Codex → OpenCode

### 已完成 ✅
- [x] <task> — <结果>

### 遇到问题 ⚠️
- <problem>

### 需要你做 📋
- [ ] <task for OpenCode>

### 文件变更 📝
- <file>: <change>
```

## 调用方式

OpenCode 通过 `codex-chat.sh` 注入 Codex 聊天窗口：

```bash
~/.claude/skills/codex-chat/codex-chat.sh "$opencode <消息>"
```

或通过 brain `/codex` 技能：

```bash
bash /Volumes/金阳/brain/scripts/codex.sh "<消息>"
```

## 硬性规则

1. **标签 = 发送方** — `$opencode` = OpenCode 发的，`/codex` = Codex 发的
2. **绝不丢失上下文** — 每次通信带全量状态
3. **绝不静默失败** — 遇问题必报告
4. **任务闭环** — 每个待办有完成确认或阻塞原因
5. **验证优先** — 收到对方完成报告后必须验证

## 错误处理

| 场景 | 处理 |
|------|------|
| Codex 没回复 | 等 30s，重试一次，仍无则报告用户 |
| Codex 回复无 `/codex` | 提醒补标签，视为有效回复 |
| Codex 声称完成但验证失败 | 告知具体失败点，要求修复 |
| Codex 报告阻塞 | 评估并给替代方案或请求用户决策 |
