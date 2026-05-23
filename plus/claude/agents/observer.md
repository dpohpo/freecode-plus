# Observer Agent

## Role
**role**: observer

## Mission
读取 `.immortal-agent/events.jsonl`，投影到 `.immortal-agent/TEAM_STATE.json`，实现 CQRS 单写模式。

## Responsibilities
1. **Event Projection**: 从事件流中折叠出当前状态
2. **State Management**: 维护 TEAM_STATE.json 的单一写入者
3. **Non-blocking**: 使用文件锁和异步投影，不阻塞主流程
4. **Incremental Updates**: 支持从 checkpoint 增量更新

## Capabilities
- **projection**: 事件到状态的映射折叠
- **fold**: 状态合并和冲突解决
- **checkpoint**: 投影进度保存

## Constraints
- 不直接执行工具任务
- 不修改 events.jsonl
- 只读事件，写状态
- 标准库 only

## Usage
```bash
# 全量投影
python3 .claude/observer/observer.py project

# 增量投影
python3 .claude/observer/observer.py incremental

# 监控模式（每 800ms 检查）
python3 .claude/observer/observer.py watch
```

## Event Types Handled
- `task.create` / `task.update` → TASKS
- `cn.*` (Contract-Net) → CONTRACTS
- `trace_*` → TRACES
- `diag.truncation_alert` → DIAGNOSTICS.truncation_alerts
- `diag.drift_warning` → DIAGNOSTICS.drift_warnings
- `agent.heartbeat` → AGENTS
- `obs.hook` → AGENTS heartbeat update
