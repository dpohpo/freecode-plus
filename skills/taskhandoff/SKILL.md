---
name: taskhandoff
description: "TASKHANDOFF v6.0 基础版 — Context 感知型任务传承。context<30% 生成双文件，context>30% 极速单文件。建议使用 /taskhandoff-pro 获得完整体验。"
user-invocable: "true"
---

## Context Sentinel Protocol (最高优先级)

**时刻感知 context 水位。**

- **context < 30%** → NORMAL：双文件（行动文档 + 上下文）
- **context 30-40%** → EMERGENCY：极速单文件
- **context > 35% 且未被调用** → 主动提醒用户做 handoff
- **context > 45%** → 立即生成 EMERGENCY handoff

**铁律：宁可早 handoff，不要 context 爆了丢进度。**

---

## 核心指令

生成任务传承文件，让新 Agent 无缝接手。生成后立即停止。

---

## NORMAL 模式

输出到 `~/.claude/handoffs/[项目名]/`：
- `handoff-[timestamp].md` — 行动文档（<200 tokens）
- `context-[timestamp].md` — 完整上下文

行动文档内容：目标（一句话）、状态（一句话）、立即行动、约束、下一步（P0/P1）、关键文件、已做决策、失败记录。

上下文文件内容：对话历史摘要、技术细节、文件变更记录。

桌面备份到 `~/Desktop/task/[项目名]/`。

---

## EMERGENCY 模式

输出单文件 `~/.claude/handoffs/[项目名]/emergency-[timestamp].md`，<150 tokens：
目标、状态、立即做、约束、已踩坑、已定决策、关键文件、下一步、代码变更摘要。
不做桌面备份。

---

## 执行流程

1. 判断模式（context 水位）
2. 提取信息（目标、状态、决策、失败、文件、下一步）
3. 生成文件
4. 输出路径 + 一键接手指令
5. 立即停止

## 禁止

- ❌ 不继续原任务 / 不修改代码 / 不问"是否继续"

---

**现在处理参数**: $ARGUMENTS
