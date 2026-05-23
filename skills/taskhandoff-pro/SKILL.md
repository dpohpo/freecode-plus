---
name: taskhandoff-pro
description: "TASKHANDOFF v6.0 — Context 感知型任务传承。双模式：NORMAL（context<30%）精细传承 / EMERGENCY（context>30%）极速传承。主动感知 context 水位，35% 时提醒用户。"
user-invocable: "true"
---

## Context Sentinel Protocol (最高优先级)

**你必须时刻感知 context 水位。** Claude Code 左下角显示 context 百分比。

规则：
- **context < 30%** → NORMAL 模式：生成完整双文件架构
- **context 30-40%** → EMERGENCY 模式：生成极速单文件，只保留核心信息
- **context > 35% 且用户未调用此技能** → 主动提醒：`"context 已达 X%，建议 /taskhandoff-pro 保存进度后开新会话"`
- **context > 45%** → 无论如何立即生成 EMERGENCY handoff，不等用户指令

**铁律：宁可早做 handoff 浪费一次，也不要 context 爆了丢失所有进度。**

---

## 核心指令

你的唯一任务：生成任务传承文件，让全新 Agent 无缝接手。
生成完毕后 **立即停止**，不继续执行原任务。

---

## NORMAL 模式（context < 30%）

### 输出文件
```
~/.claude/handoffs/[项目名]/
├── handoff-[YYYYMMDD-HHMMSS].md     ← 行动文档（<200 tokens）
├── handoff-[YYYYMMDD-HHMMSS].json   ← 结构化状态
└── context-[YYYYMMDD-HHMMSS].md     ← 完整上下文

~/Desktop/task/[项目名]/              ← 桌面备份（全部文件同步）
```

### 行动文档模板（必须 <200 tokens）

```markdown
# [项目名] Handoff v6.0

> 时间: YYYY-MM-DD HH:MM | 上下文: context-[timestamp].md

## 目标
[一句话：用户要什么 + 成功标准]

## 状态
[一句话：完成了什么 / 进度百分比 / 当前卡在哪]

## 立即行动
[新 Agent 的第一步：动词+对象+具体路径]

## 约束
1. [不能做什么]
2. [技术限制]
3. [已踩的坑 — 不要重复]

## 下一步
- P0: [必须做] → 验收: [标准]
- P1: [应该做] → 验收: [标准]

## 关键文件
- [路径1] — [状态/说明]
- [路径2] — [状态/说明]

## 已做决策（不要推翻）
- D1: [选择了X而非Y，因为Z]
- D2: [选择了A而非B，因为C]

## 失败记录（不要重蹈）
- [尝试X → 失败原因 → 教训]
```

### JSON 状态文件
```json
{
  "version": "6.0",
  "project": "[项目名]",
  "generated_at": "ISO-8601",
  "context_file": "context-[timestamp].md",
  "context_usage_at_handoff": "XX%",
  "mode": "NORMAL|EMERGENCY",
  "objective": "[目标]",
  "status": "in_progress",
  "progress": {"done": X, "total": Y},
  "next_action": "[立即行动]",
  "constraints": ["..."],
  "decisions": [{"id": "D1", "choice": "...", "reason": "..."}],
  "failures": [{"what": "...", "why": "...", "lesson": "..."}],
  "files": [{"path": "...", "status": "...", "note": "..."}],
  "next_steps": [{"priority": "P0", "task": "...", "acceptance": "..."}]
}
```

### 完整上下文文件
```markdown
# [项目名] 完整上下文

> 关联行动文档: handoff-[timestamp].md
> 用途: 新 Agent 遇到疑问时查阅

## 对话历史摘要
[按时间线记录关键交互，不需要逐字转录，但要保留：]
- 用户的每个关键需求/指令
- Agent 的关键决策和行动
- 重要的搜索结果/发现
- 代码修改记录（文件+变更内容）
- 错误和修复过程

## 技术细节
- 技术栈选择及理由
- 架构设计及演进
- 已验证的方案/库

## 文件变更记录
[每个被修改/创建的文件：路径 + 做了什么 + 为什么]
```

---

## EMERGENCY 模式（context > 30%）

**极速生成，只输出一个文件，不做桌面备份。**

### 输出：单个 md 文件
```
~/.claude/handoffs/[项目名]/emergency-[YYYYMMDD-HHMMSS].md
```

### EMERGENCY 模板（必须 <150 tokens + 关键 context）

```markdown
# EMERGENCY HANDOFF - [项目名]

> 时间: YYYY-MM-DD HH:MM | context 已达 XX%

**目标**: [一句话]
**状态**: [一句话]
**立即做**: [具体动作]

**约束**: [逗号分隔的关键限制]
**已踩坑**: [逗号分隔的失败教训]
**已定决策**: [逗号分隔的不可推翻决策]

**关键文件**:
[路径列表 + 一词状态]

**下一步**:
1. [P0任务 → 验收标准]
2. [P1任务 → 验收标准]

**代码变更摘要**:
[哪些文件改了什么，用最精简的语言]
```

---

## 执行流程

1. **判断模式** — 根据 context 水位选择 NORMAL 或 EMERGENCY
2. **提取信息** — 从对话历史中提取：目标、状态、决策、失败、文件、下一步
3. **生成文件** — 按对应模板生成
4. **NORMAL 追加**：创建 JSON + context 文件 + 桌面备份
5. **输出路径** — 显示文件位置 + 一键接手指令
6. **立即停止**

### 输出格式
```
✅ Handoff 已生成 [NORMAL/EMERGENCY]

📁 [文件路径列表]

🔗 接手指令（复制给新 Agent）:
═══════════════════════════
读取 [handoff路径] → 执行"立即做"→ 疑问查阅 [context路径]
═══════════════════════════
```

---

## 禁止

- ❌ 不继续执行原任务
- ❌ 不修改代码
- ❌ 不问"是否继续"
- ❌ EMERGENCY 模式下不做桌面备份（省 context）
- ❌ 不要在模板里加装饰性内容（ASCII art、feature 列表等）

---

**现在处理参数**: $ARGUMENTS
