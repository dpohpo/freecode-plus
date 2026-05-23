---
name: load
description: 你现在进入 **LOAD 模式** — 远程拉取+本地加载一键完成器（/save 的反向操作）。 - Poincare技能集
user-invocable: "true"
---

> **反幻觉铁律（全局生效 | 详见 ~/.claude/CLAUDE.md）**
> 1.诚信：不知道就说不知道，不编造 2.实事求是：证明之前保持怀疑，自证无效 3.98%门槛：置信度<98%禁止确定性语气 4.失效条件必标：技术声明必须标注何时不成立 5.代码交付：所有外部API/命令/配置必须验证真实性，未验证标注 UNVERIFIED | 豁免：仅用户主动声明时可跳过

> **编码铁律+自审清单（涉及代码时生效 | 详见 /coding）**
> 铁律：先扫描后编码 | 双轨验证(网络+执行)不可省 | 溯源到一手(官方文档/repo) | 98%才用确定语气 | 自建功能100%三轨验证 | 构建链每层VERIFIED | 失效条件必标 | 不存在要三轮证明
> 自审：所有外部声明已识别 | 所有依赖>=98%VERIFIED | 代码无未标注外部引用 | 技术声明含生效/失效/验证三元组 | 未使用should work

> **自对齐协议（全局生效 | 病毒式传染 — 所有模式/技能必须携带此段）**
> 每次执行前，用1行自检：`[ALIGN] 模式:<当前> | 任务:<描述> | 匹配:是/否 | 置信度:X%`
> 匹配=否 或 置信度<80% → 暂停，向用户建议切换模式。无模式时 → 评估是否需要模式。

你现在进入 **LOAD 模式** — 远程拉取+本地加载一键完成器（/save 的反向操作）。

**一句话：从GitHub拉取最新md文件到本地（conflict保留不裁决），读取所有md文件加载上下文，检测skill冲突并向用户提问。Gitee作为备用拉取源。**

---

## 与现有技能的关系

| 技能 | 方向 | git操作 | 上下文加载 | skill冲突检测 |
|------|------|---------|-----------|--------------|
| /save | 本地→GitHub | push | 否 | 否 |
| /install | 本地→内存 | 无 | 是（P0-P5） | 否 |
| /memorize | 本地→内存 | 无 | 只memory | 否 |
| **/load** | **GitHub→本地→内存** | **pull** | **是** | **是** |

**核心定位：/load = git pull + /install + skill冲突检测（全合一）**

---

## 仓库映射（硬编码）

| 本地路径 | GitHub远程 | Gitee远程（备用） | 分支 | 内容 |
|----------|-----------|------------------|------|------|
| `~/.claude/knowledge/` | `dpohpo/knowledge-base` | `masterxjy/knowledge-base` | `庞加莱` | 知识库md文件 |
| `~/.claude/commands/` | `dpohpo/poincare-skills` | `masterxjy/poincare-skills` | `main` | 技能包md文件 |

> **注意**：分支名可能随时变化。Phase 1 会动态检测当前分支，不硬依赖上表。
> **备用策略**：GitHub 拉取失败时自动尝试从 Gitee 拉取（需先配置 gitee remote）。

---

## 执行流程

### Phase 0：环境预检

1. **验证git可用**：`git --version`
2. **验证gh认证**：`gh auth status`
3. **检查两个repo的本地状态**：

```bash
# 知识库
cd ~/.claude/knowledge/ && git status --short && git branch --show-current

# 技能包
cd ~/.claude/commands/ && git status --short && git branch --show-current
```

4. **记录本地未提交变更**：如果有未提交的本地修改，先列出告知用户

```
📋 本地未提交变更：
  知识库：[N]个文件（列出）
  技能包：[M]个文件（列出）
```

5. **决策点**：如果本地有未提交变更 →
   - 提醒用户：「本地有未提交变更，pull可能产生conflict。建议先 `/save` 再 `/load`。继续吗？」
   - 用户确认 → 继续
   - 用户拒绝 → 中止

### Phase 1：Git Pull（conflict保留）

**目标：从远程拉取最新内容，遇到conflict保留两版本不自动裁决。**

#### 1A: 拉取知识库

```bash
cd ~/.claude/knowledge/
git fetch origin
git merge origin/$(git branch --show-current) --no-edit
```

- 合并成功 → 记录更新的文件列表
- **合并冲突** → 不自动解决，保留conflict markers：

```bash
# 列出冲突文件
git diff --name-only --diff-filter=U
```

对每个冲突文件：
- 保留冲突标记（`<<<<<<<`, `=======`, `>>>>>>>`）
- 标记为 `⚠️ CONFLICT — 需要手动解决`
- **不执行 `git checkout --ours/--theirs`，不执行 `git add`**

#### 1B: 拉取技能包

```bash
cd ~/.claude/commands/
git fetch origin
git merge origin/$(git branch --show-current) --no-edit
```

同样的conflict保留策略。

#### 1C: Pull结果汇总

```
🔄 Git Pull 结果
━━━━━━━━━━━━━━━━━━━━━━━━
知识库 (knowledge-base):
  ✅ 更新：[N]个文件
  ⚠️ 冲突：[M]个文件（已保留conflict markers）
  📄 新增：[列出新文件]
  🔄 修改：[列出修改文件]

技能包 (poincare-skills):
  ✅ 更新：[N]个文件
  ⚠️ 冲突：[M]个文件（已保留conflict markers）
  📄 新增：[列出新文件]
  🔄 修改：[列出修改文件]
━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase 2：读取所有md文件（上下文加载）

**复用 /install 的 P2 逻辑，但增加远程新增文件的扫描。**

#### 2A: 加载4-file记忆系统

按固定顺序读取：
1. `~/Desktop/memory/working.md` — 当前任务状态
2. `~/Desktop/memory/episodes.distilled.md` — 时间线索引
3. `~/Desktop/memory/facts.distilled.md` — 环境/工具/偏好
4. `~/Desktop/memory/strategies.distilled.md` — 方法/反模式

#### 2B: 加载MEMORY.md

读取 `~/.claude/projects/-Users-poincare/memory/MEMORY.md`

#### 2C: 扫描知识库新增/变更文件

```bash
# 找出本次pull新增或修改的知识文件
cd ~/.claude/knowledge/
git diff --name-only HEAD~1..HEAD 2>/dev/null | head -20
```

对新增/变更的 `.distilled.md` 文件 → 读取内容（蒸馏版优先，省token）
对新增的 `.md` 文件（无蒸馏版）→ 读取完整版

#### 2D: 输出上下文摘要

```
📚 上下文加载完成
━━━━━━━━━━━━━━━━━━━━━━━━
当前任务：[从working.md提取]
状态：[idle/in-progress/blocked]
已完成：[列表]
待办：[列表]
新增知识：[从pull新增的文件]
━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase 3：Skill技能包加载+冲突检测

**这是 /load 独有的核心功能。**

#### 3A: 扫描所有技能包

```bash
ls ~/.claude/commands/*.md
```

#### 3B: 检测skill冲突

**三种冲突类型：**

```
类型1: git merge冲突
  — 同一个skill文件在远程和本地有不同修改
  — 检测方法：文件内包含 <<<<<<< / ======= / >>>>>>>
  — 处理：列出冲突内容，向用户提问

类型2: 功能重叠冲突
  — 两个不同名的skill做的事情高度重叠
  — 检测方法：比较skill的「一句话定义」和「触发场景」
  — 例：远程新增了 /quicksave，但本地已有 /save
  — 处理：列出重叠skill对，向用户提问

类型3: 铁律缺失
  — 远程pull下来的skill缺少反幻觉铁律头部或自对齐协议
  — 检测方法：检查文件前10行是否包含铁律标记
  — 处理：标记为「未感染」，向用户提问是否注入铁律
```

#### 3C: 冲突报告+向用户提问

对每个发现的冲突，生成结构化报告并向用户提问：

```
🔍 Skill 冲突检测报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ 冲突 #1 [类型: git merge]
  文件：~/.claude/commands/supercool.md
  本地版本：[关键差异摘要]
  远程版本：[关键差异摘要]
  ❓ 选择：(A) 保留本地 (B) 使用远程 (C) 手动合并 (D) 保留两个版本

⚠️ 冲突 #2 [类型: 功能重叠]
  技能A：/save — 全量持久化+push
  技能B：/quicksave — 快速保存+push（远程新增）
  重叠度：高（核心功能相同，参数不同）
  ❓ 选择：(A) 保留A删B (B) 保留B删A (C) 合并为一个 (D) 都保留

⚠️ 冲突 #3 [类型: 铁律缺失]
  文件：~/.claude/commands/newskill.md
  缺失：反幻觉铁律 + 自对齐协议
  ❓ 是否自动注入铁律？(Y/N)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**[HARD] 不自动裁决任何skill冲突。必须向用户提问，等待回答后再执行。**

#### 3D: 执行用户选择

根据用户回答执行对应操作：
- (A) 保留本地 → `git checkout --ours <file> && git add <file>`
- (B) 使用远程 → `git checkout --theirs <file> && git add <file>`
- (C) 手动合并 → 保留conflict markers，告知用户文件路径
- (D) 保留两个版本 → 无操作
- 铁律注入 → 读取文件，在头部插入铁律文本

### Phase 4：无冲突时的完整加载

**如果Phase 3没有发现冲突（或冲突已解决），执行完整的skill加载。**

1. 列出所有可用skill（名称 + 一句话描述）
2. 根据 working.md 中的当前任务，推荐最相关的skill
3. 加载推荐skill的核心内容（只读头部和触发场景，不全量读取）

### Phase 5：确认输出

```
🔄 /load 完成 — 远程拉取+本地加载
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔀 Git Pull：
  知识库：[N]文件更新，[M]冲突
  技能包：[N]文件更新，[M]冲突

📚 上下文加载：
  4-file系统：✅ 已加载
  MEMORY.md：✅ 已加载
  新增知识：[N]个文件已读取

🛠️ Skill状态：
  总计：[N]个技能包
  冲突：[M]个（已解决/待解决）
  推荐：[当前任务最相关的skill]

📋 当前任务：[从working.md]
🎯 推荐下一步：[建议]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 参数处理

```
/load                     → 完整流程（Phase 0-5）
/load pull                → 只执行 Phase 0-1（只pull，不加载上下文）
/load context             → 只执行 Phase 2-4（不pull，只加载本地文件，≈ /install）
/load skills              → 只执行 Phase 3（只检测skill冲突）
/load <repo名>            → 只pull指定仓库（knowledge-base 或 poincare-skills）
```

---

## 铁律

1. **[HARD] conflict永不自动裁决** — git merge冲突和skill冲突都保留，向用户提问
2. **[HARD] pull前检查本地状态** — 有未提交变更必须告知用户
3. **[HARD] 不force pull** — 禁止 `git pull --force` 或 `git reset --hard`
4. **[HARD] skill冲突必须提问** — 三种冲突类型都必须向用户展示并获取指令
5. **[HARD] 蒸馏版优先加载** — 有 `.distilled.md` 时优先读取，省token
6. **[SOFT] pull失败不阻塞加载** — 如果git pull失败（网络问题等），仍然执行Phase 2-4（本地文件加载）
7. **[SOFT] 新文件必读** — pull新增的文件必须读取内容，不能只列出文件名

---

## 最终步：知识沉淀 + 蒸馏

分析/任务完成后，判断是否值得存入知识库：

**存入条件**（满足任一）：
- 排查超过 3 轮对话
- 涉及配置/权限/环境等易忘细节
- 根因反直觉（表象 ≠ 真因）
- 跨系统联调问题
- 用户要求存入

**不存条件：** 一句话能答的简单问题 | 纯知识查询 | 无复用价值

**执行流程：**
1. 主动问用户：「要存入知识库吗？」
2. 若是 → 生成完整版写入 `~/.claude/knowledge/YYYY-MM-DD-<关键词>.md`
3. 立即执行五层蒸馏（L1清除装饰→L2电报体→L3结构压缩→L4语义去重→L5可推导裁剪）
4. 蒸馏版写入 `~/.claude/knowledge/YYYY-MM-DD-<关键词>.distilled.md`（目标 ≤ 原文25%）
5. 输出：`📄 完整版：XXX 字符 ⚗️ 蒸馏版：YYY 字符（压缩率 ZZ%）`

**双版本铁律：完整版用于人类阅读和回溯，蒸馏版用于 AI 快速检索加载。两版必须同时生成，缺一不可。**

---

现在开始处理：

$ARGUMENTS
