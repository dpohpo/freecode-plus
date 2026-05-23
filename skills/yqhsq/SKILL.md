---
name: yqhsq
description: 一气化三清 — 使用 Free Code 官方 Agent Teams 创建六个 teammate。
user-invocable: "true"
---

# 一气化三清

本技能只使用 Free Code 官方 Agent Teams 机制。

不要启动旧的 hcom/tmux 七窗脚本。不要让任何成员主动 `hcom send` 报到。不要让 lead 给自己发消息。

## 官方工作流

1. 使用 `TeamCreate` 创建 team。
2. 使用 `Agent` 工具创建 teammate。
3. 创建 teammate 时必须传 `name`、`team_name` 和 `subagent_type`。
4. `subagent_type` 必须与 `name` 相同，让 Free Code 加载对应 `~/.claude/agents/<name>.md` 作为角色 system prompt。
5. 不显式传 `model`，除非用户点名要求；模型继承由 Free Code teammate spawn 流程处理。
6. `Agent` 的 `prompt` 就是初始 mailbox 消息；不要再用 shell 或 hcom 发送。
7. 后续沟通使用 `SendMessage`，消息会自动投递；不要手动查 inbox。

这对应 Free Code 上游设计：spawn 命令自身不带 prompt，leader 将初始任务写入 teammate mailbox；teammate 的 inbox poller 自动接收并执行。

## 固定六个 teammate

- `yuanshi`: `subagent_type=yuanshi`，Planner，负责方案拆解、约束、验收标准、风险边界。
- `lingbao`: `subagent_type=lingbao`，Executor，负责实现可行性、命令执行、文件产出、落地路径。
- `daode`: `subagent_type=daode`，Critic，负责审查、测试、反例、回归风险、验收门控。
- `guanmiao`: `subagent_type=guanmiao`，Observer，负责事实同步、外部状态、上下文遗漏。
- `siguo`: `subagent_type=siguo`，ErrorScribe，负责错误模式、失败链路、复盘、防复发。
- `xuanshu`: `subagent_type=xuanshu`，CodexDetector，负责 Codex/CLI/ACP/外部工具链状态。

## 执行规则

如果用户同时给出任务，直接创建 team 并把任务拆给六个 teammate。每个 teammate 的 `Agent` prompt 必须包含目标、边界、输入、输出格式和验证方式。

如果用户只是召唤团队，创建六个 teammate，但每个 prompt 只要求待命：

```text
你已加入当前 team。不要开始业务任务。等待 team lead 通过 SendMessage 或 task list 分派任务。
```

## 禁止事项

- 禁止运行 `~/.claude/skills/yqhsq/scripts/launch.sh`
- 禁止运行 `hcom list`
- 禁止运行 `hcom send`
- 禁止启动外部七窗来模拟 teammate
- 禁止太一/lead 给自己发消息
- 禁止手写 roster 覆盖 Free Code team config
