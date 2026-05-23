---
name: taskhandoff-extreme
description: "TASKHANDOFF v6.0 极限版 — Context 感知型任务传承。与 pro 版相同的 context 感知机制，但额外提供自适应压缩和增量 delta 传输。"
user-invocable: "true"
---

## Context Sentinel Protocol (最高优先级)

**时刻感知 context 水位。**

- **context < 30%** → NORMAL：双文件 + 自适应压缩 + delta 传输
- **context 30-40%** → EMERGENCY：极速单文件
- **context > 35% 且未被调用** → 主动提醒用户做 handoff
- **context > 45%** → 立即生成 EMERGENCY handoff

**铁律：宁可早 handoff，不要 context 爆了丢进度。**

---

## 核心指令

生成任务传承文件，让新 Agent 无缝接手。生成后立即停止。

---

## NORMAL 模式（带自适应压缩）

输出到 `~/.claude/handoffs/[项目名]/`：
- `handoff-[timestamp].md` — 行动文档（<200 tokens）
- `handoff-[timestamp].json` — 结构化状态
- `context-[timestamp].md` — 完整上下文

### 自适应压缩规则
- 目标/约束：0% 压缩（完整保留）
- 关键决策：10-20% 压缩
- 文件信息：50% 压缩（只保留路径+状态+关键变更）
- 示例/参考：70-90% 压缩（只保留结论）
- 对话历史：智能摘要（保留关键转折点）

### 增量 Delta
如果存在上一次 handoff 文件，只传输变化部分：
- `delta-[timestamp].md` — 相对于上次 handoff 的增量

### 行动文档内容
目标、状态、立即行动、约束、下一步（P0/P1）、关键文件、已做决策、失败记录。

### 上下文文件内容
对话历史摘要、技术细节、文件变更记录、压缩决策日志。

桌面备份到 `~/Desktop/task/[项目名]/`。

---

## EMERGENCY 模式

与 pro 版完全相同：单文件 `emergency-[timestamp].md`，<150 tokens。
不做桌面备份、不做 delta 计算。

---

## 执行流程

1. 判断模式（context 水位）
2. 提取信息 + 应用自适应压缩
3. 检查是否有上次 handoff（有则生成 delta）
4. 生成文件
5. 输出路径 + 一键接手指令
6. 立即停止

## 禁止

- ❌ 不继续原任务 / 不修改代码 / 不问"是否继续"

---

**现在处理参数**: $ARGUMENTS
