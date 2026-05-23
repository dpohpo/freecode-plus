# /yqhsq — 一气化三清

使用 Free Code 官方 Agent Teams 机制。不要运行 `hcom`，不要运行 `~/.claude/skills/yqhsq/scripts/launch.sh`，不要让任何 agent 主动发启动报到消息。

## 默认动作

收到 `/yqhsq`、`五神`、`七神`、`一气化三清`、`让 team agent 做` 等请求时：

1. 如果当前还没有 team context，先调用 `TeamCreate` 创建 team。
2. 使用 `Agent` 工具创建六个 teammate。必须使用 `name`、`team_name`、`subagent_type` 参数；不要用 shell/tmux/hcom 手动开窗口。
3. `subagent_type` 必须与 `name` 相同，让 Free Code 加载对应 `~/.claude/agents/<name>.md` 作为角色 system prompt。
4. 不要显式传 `model`，除非用户点名要求。模型继承由 Free Code 的 teammate spawn 流程处理。
5. 初始任务通过 `Agent(... prompt=...)` 写入 teammate mailbox；不要用 `hcom send`。
6. 后续沟通使用 `SendMessage` 工具；不要给自己发消息，不要给 `team-lead` 发自我指令。

## 固定成员

- `yuanshi`: `subagent_type=yuanshi`，Planner，负责方案拆解、约束、验收标准、风险边界。
- `lingbao`: `subagent_type=lingbao`，Executor，负责实现可行性、命令执行、文件产出、落地路径。
- `daode`: `subagent_type=daode`，Critic，负责审查、测试、反例、回归风险、验收门控。
- `guanmiao`: `subagent_type=guanmiao`，Observer，负责事实同步、外部状态、上下文遗漏。
- `siguo`: `subagent_type=siguo`，ErrorScribe，负责错误模式、失败链路、复盘、防复发。
- `xuanshu`: `subagent_type=xuanshu`，CodexDetector，负责 Codex/CLI/ACP/外部工具链状态。

## 用户给了任务时

直接把任务拆给六个 teammate。每个 `Agent` prompt 必须包含：

- 任务目标
- 该成员的审查/执行视角
- 输入文件或上下文
- 期望输出格式
- 验证方式

创建后等待 teammate 结果自动回到当前会话；不要手动查 hcom inbox。

## 用户只是召唤团队时

创建 team 和六个 teammate，但每个 teammate 的 prompt 只要求：

```text
你已加入当前 team。不要开始业务任务。等待 team lead 通过 SendMessage 或 task list 分派任务。
```

## 禁止

- 禁止 `bash ~/.claude/skills/yqhsq/scripts/launch.sh`
- 禁止 `hcom list`
- 禁止 `hcom send`
- 禁止太一/lead 给自己发消息
- 禁止手写外部 roster 覆盖 Free Code 的 team config
- 禁止把 teammate 当普通终端窗口管理

## 依据

Free Code 官方流程是：`TeamCreate` 建队，`Agent(name, team_name, subagent_type, prompt)` 创建 teammate，启动进程不带 prompt，初始任务写入 mailbox，后续由 `SendMessage` 和 inbox poller 自动投递。
