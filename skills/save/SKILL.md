---
name: save
description: 你现在进入 **SAVE 模式** — 全量持久化+远程备份一键完成器。 - Poincare技能集
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

你现在进入 **SAVE 模式** — 全量持久化+远程备份一键完成器。

**一句话：整合当前会话（含sub-agent）所有内容，去重保留conflict，写入所有重要md文件，然后push到GitHub+Gitee（备用仓库）。**

---

## 与现有技能的关系

| 技能 | 写入范围 | push | /save中的角色 |
|------|---------|------|--------------|
| /memory | memory.md + 4-file系统 | 否 | Phase 2 调用其逻辑 |
| /md | ~/.claude/knowledge/ | 否 | Phase 3 调用其逻辑 |
| /backup | 技能包copy | 否 | 不调用 |
| **/save** | **全部 + MEMORY.md** | **是** | **统一入口** |

**核心定位：/save = /memory + /md路由 + MEMORY.md同步 + git push（全合一）**

---

## 执行流程

### Phase 0：内容收集与整合

**目标：扫描当前会话（含sub-agent输出）的全部有价值内容**

1. **回溯当前会话**，从session开始（或上一次 /save 调用位置）到当前位置
2. **识别sub-agent输出**：
   - 搜索会话中所有 Task tool 调用的返回结果
   - 识别 Team 协作中的 SendMessage 内容
   - 识别 background task 的输出
3. **提取内容分类**：

```
📦 内容清单（逐项列出）
━━━━━━━━━━━━━━━━━━━━━━━
A. 新发现的事实（VERIFIED/UNVERIFIED标注）
B. 做出的决策及理由
C. 创建/修改的文件清单
D. 代码变更摘要
E. 踩过的坑与解决方案
F. 未完成事项(TODO)
G. 用户态度与偏好（引用原话）
H. 新知识/教训（值得进knowledge/的）
I. 团队状态（如有agent team）
```

4. **去重规则**：
   - 多个sub-agent报告同一事实 → 保留信息最完整的版本
   - 同一决策在主线程和sub-agent中都出现 → 保留主线程版本（用户直接参与的）
   - **冲突处理：同一事实的不同版本 → 全部保留，标注 `⚠️ CONFLICT`**

```
⚠️ CONFLICT: [主题]
  版本A（来源：[主线程/agent-X]）：[内容]
  版本B（来源：[主线程/agent-Y]）：[内容]
  → 未裁决，两版本均保留
```

### Phase 1：冲突检测（新内容 vs 已有记忆）

**读取已有记忆进行交叉比对，按 /memory 的 2.5 步冲突检测协议执行。**

1. 读取 `~/Desktop/memory/working.md`（当前状态）
2. 读取 `~/.claude/projects/-Users-poincare/memory/MEMORY.md`（全局索引）
3. 逐项比对 Phase 0 提取的内容与已有记忆：
   - 🟢 一致 → 跳过（不重复写入）
   - 🟡 演化 → 标注：`⟳ 更新：[旧状态] → [新状态]`
   - 🔴 冲突 → 全部保留，标注 `⚠️ CONFLICT`（不裁决，让用户/未来session决定）

### Phase 2：写入情景记忆（/memory 逻辑）

**执行 /memory 的完整写入流程，写入以下文件：**

| 文件 | 路径 | 操作 |
|------|------|------|
| memory.md | ~/Desktop/memory.md | APPEND 新 segment |
| memorydistillation.md | ~/Desktop/memorydistillation.md | APPEND 蒸馏段 |
| working.md | ~/Desktop/memory/working.md | OVERWRITE（最新状态）|
| episodes.md | ~/Desktop/memory/episodes.md | APPEND 新条目 |
| facts.md | ~/Desktop/memory/facts.md | APPEND（如有新事实）|
| strategies.md | ~/Desktop/memory/strategies.md | APPEND（如有新策略）|
| 对应 .distilled.md | 同目录 | 从 .md 重新生成 |

### Phase 3：写入知识库（/md 逻辑路由）

**扫描 Phase 0 的内容，判断是否有值得进知识库的内容。**

判断标准：
- 排查超过3轮的问题解决过程 → 存
- 反直觉的根因发现 → 存
- 新工具/框架的使用经验 → 存
- 跨系统联调经验 → 存
- 一句话能说清的 → 不存

如有值得存入的内容：
1. 写入 `~/.claude/knowledge/YYYY-MM-DD-<关键词>.md`（完整版）
2. 执行五层蒸馏，写入 `.distilled.md`
3. 检查知识进化：与已有知识的关系（创建/合并/泛化/失效）

**如果没有值得进知识库的内容 → 跳过此Phase，不强制生成。**

### Phase 4：更新 MEMORY.md（全局索引）

**更新 `~/.claude/projects/-Users-poincare/memory/MEMORY.md`**

MEMORY.md 是全局索引文件，需要保持精简（≤200行）。更新规则：

1. 读取当前 MEMORY.md
2. 根据 Phase 0-3 的结果，更新以下段落：
   - **活跃项目** — 有变化才更新
   - **待决事项** — 反映最新 TODO
   - **关键教训** — 追加新教训（如有）
   - **知识库索引** — 追加新知识文件（如有）
3. **去重**：MEMORY.md 中已有的信息不重复添加
4. **conflict保留**：如果新内容与MEMORY.md已有内容冲突，两版本都保留，标注 `⚠️ CONFLICT`
5. **行数控制**：如超过200行，提醒用户精简

### Phase 5：Git Push 到 GitHub + Gitee（备用仓库）

**将所有变更 push 到对应的 GitHub 和 Gitee 仓库。**

#### 5A: 知识库 push

```bash
cd ~/.claude/knowledge/
git add -A
git commit -m "save: [简要描述本次变更] — $(date +%Y-%m-%d_%H:%M)"

# GitHub 主仓库
git push origin 庞加莱

# Gitee 备用仓库（如果配置）
git remote | grep -q gitee && git push gitee 庞加莱 || echo "Gitee remote 未配置，跳过"
```

- GitHub 远程：`dpohpo/knowledge-base`
- Gitee 远程：`masterxjy/knowledge-base`（需手动添加 remote）
- 分支：`庞加莱`
- 如果 push 失败 → 报告错误，不强制 push

#### 5B: 技能包 push

```bash
cd ~/.claude/commands/
git add -A
git commit -m "save: [简要描述本次变更] — $(date +%Y-%m-%d_%H:%M)"

# GitHub 主仓库
git push origin 庞加莱

# Gitee 备用仓库（如果配置）
git remote | grep -q gitee && git push gitee 庞加莱 || echo "Gitee remote 未配置，跳过"
```

- GitHub 远程：`dpohpo/poincare-skills`
- Gitee 远程：`masterxjy/poincare-skills`（需手动添加 remote）
- 分支：`庞加莱`
- 如果 push 失败 → 报告错误，不强制 push

#### 5C: 添加 Gitee remote（首次使用）

如果 Gitee remote 未配置，执行：

```bash
# 知识库
cd ~/.claude/knowledge/
git remote add gitee git@gitee.com:masterxjy/knowledge-base.git

# 技能包
cd ~/.claude/commands/
git remote add gitee git@gitee.com:masterxjy/poincare-skills.git
```

#### 5C: push 前安全检查

**[HARD] push 前必须执行：**
- `git diff --staged` 确认没有敏感信息（API key、token、密码）
- 如果发现敏感信息 → 中止 push，提醒用户运行脱敏工具
- `git status` 确认没有意外文件被加入

### Phase 6：确认输出

写入完成后，输出结构化确认：

```
🔄 /save 完成 — 全量持久化+远程备份
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 内容统计：
  - 扫描范围：[起点] → [终点]
  - 去重：[N]项重复已合并
  - 冲突：[M]项保留（⚠️ CONFLICT标注）

📄 文件更新：
  ✅ ~/Desktop/memory.md — Segment #[N] 追加
  ✅ ~/Desktop/memorydistillation.md — 蒸馏段追加
  ✅ ~/Desktop/memory/working.md — 覆写
  ✅ ~/Desktop/memory/episodes.md — 追加
  [✅/⏭️] ~/Desktop/memory/facts.md — [追加/无新事实]
  [✅/⏭️] ~/Desktop/memory/strategies.md — [追加/无新策略]
  [✅/⏭️] ~/.claude/knowledge/... — [新知识文件/无需存入]
  ✅ MEMORY.md — 已同步

🚀 Git Push：
  GitHub:
    ✅ dpohpo/knowledge-base (庞加莱) — [commit hash]
    ✅ dpohpo/poincare-skills (庞加莱) — [commit hash]
  Gitee (备用):
    ✅ masterxjy/knowledge-base (庞加莱) — [commit hash 或 "未配置"]
    ✅ masterxjy/poincare-skills (庞加莱) — [commit hash 或 "未配置"]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 参数处理

```
/save                     → 执行完整流程（Phase 0-6）
/save quick               → 快速模式：跳过 Phase 3（不判断知识库），只做 memory + MEMORY.md + push
/save nopush              → 本地模式：执行 Phase 0-4，跳过 Phase 5（不push）
/save <自定义描述>         → 将描述作为 commit message 的一部分
```

---

## 铁律

1. **[HARD] 去重但不丢失** — 相同内容去重，但冲突版本全部保留，标注 `⚠️ CONFLICT`
2. **[HARD] push 前安全检查** — 禁止 push 包含敏感信息的内容
3. **[HARD] 不覆盖已有记忆** — memory.md 和 episodes.md 只 APPEND，永不覆盖历史
4. **[HARD] working.md 总是覆写** — 它代表「当前状态」，必须反映最新
5. **[HARD] MEMORY.md ≤ 200行** — 超过时提醒用户精简，不自动截断
6. **[HARD] push 失败不强制** — 禁止 `--force`，报告错误让用户处理
7. **[SOFT] 能跳过就跳过** — 如果某个文件无需更新（无新内容），不做空写入
8. **[SOFT] 五层蒸馏率 ≤ 25%** — 所有蒸馏版目标不超过完整版的 25%

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
