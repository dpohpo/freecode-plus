# SKILL.md - 极致报告生成系统 v2.0

> **Codename**: Meridian
> **Status**: Production Specification
> **Philosophy**: 报告的本质不是文字——是可追溯的决策支撑链。

---

## 触发场景

- 用户说 "/report-content" 或 "/report-content 主题"
- 用户要求生成专业报告、研究报告、决策文档
- 用户需要对某个主题进行深度分析并输出结构化文档
- 用户需要多格式报告输出（PDF/PPT/Obsidian/Notion/HTML）

---

## 0. 设计元原则

在进入任何架构细节之前，先固定三条不可妥协的元原则。所有后续设计决策必须服从这三条，冲突时按优先级排序：

**P1. 可追溯优先于详尽（Traceability > Exhaustiveness）**
一个只有 10 页但每个关键结论都能追溯到一手来源的报告，严格优于一个 100 页但引用模糊的报告。系统在 token 预算不足时，必须优先保证关键结论的证据链完整性，而非覆盖更多子话题。

**P2. 成本感知是一等公民（Cost-Awareness is First-Class）**
Anthropic 的工程实践已经证实：多智能体系统消耗的 token 量约为普通对话的 15 倍。一份深度报告可能消耗 500 万-1000 万 tokens。系统必须在每个决策点评估"边际质量提升 / 边际 token 成本"，在收益递减时主动停止或请求人类决策，而不是无限制地追求完美。

**P3. 混合架构：确定性流水线处理可预测部分，智能体处理不可预测部分（Hybrid: Pipelines for Predictable, Agents for Unpredictable）**
这是 2025 年产业界的共识：纯智能体系统不可靠、不可控、成本爆炸；纯流水线系统无法处理开放式研究。正确答案是混合——用确定性流水线处理格式渲染、引用管理、一致性检查等可预测任务，用智能体处理信息检索、证据评估、论证构建等需要推理的任务。

---

## 1. 总体架构：认知循环（Cognitive Loop）

### 1.1 为什么不是流水线

GPT v0.5 提出的 8 模块串行流水线（M0→M1→...→M7→M8）有三个致命问题：

1. **故障归因不可能**：最终报告质量差时，无法快速定位是检索质量差、大纲设计差、还是写作质量差
2. **反馈延迟过长**：直到 M6（QA Gates）才发现 M1（检索）的问题，前面所有工作白费
3. **无法增量优化**：改进其中一个模块需要重跑整条流水线

### 1.2 为什么不是纯智能体

Anthropic 自身的多智能体研究系统工程实践表明：
- token 用量解释了 80% 的性能方差——本质上是"花更多 token = 更好结果"
- 多智能体系统比单智能体好 90.2%，但也消耗约 15 倍 token
- 智能体在紧密耦合的任务（如编码）上表现不如在宽度研究任务上

报告生成混合了两种任务：宽度研究（适合智能体）和精确渲染/引用管理（适合流水线）。

### 1.3 Meridian 架构

```
┌──────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                       │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │ Checkpoint 1 │  │ Checkpoint 2 │  │ Checkpoint 3         │ │
│  │ 研究计划确认  │  │ 证据审查     │  │ 初稿审查 / 交付决策   │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬───────────┘ │
│         │                │                     │             │
├─────────┼────────────────┼─────────────────────┼─────────────┤
│         ▼                ▼                     ▼             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              COGNITIVE LOOP ENGINE                    │   │
│  │                                                      │   │
│  │   ┌───────────────────────────────────────────┐     │   │
│  │   │         LOOP CONTROLLER                    │     │   │
│  │   │  · 评估当前质量分 vs 目标质量分              │     │   │
│  │   │  · 计算边际收益率（ΔQ / ΔTokens）           │     │   │
│  │   │  · 决策：继续迭代 / 请求人类介入 / 交付      │     │   │
│  │   └───────────┬───────────────────────────────┘     │   │
│  │               │                                      │   │
│  │   ┌───────────▼───────────────────────────────┐     │   │
│  │   │         QUALITY ORACLE                     │     │   │
│  │   │  · 实时评分（不是事后检查）                   │     │   │
│  │   │  · 定位最薄弱维度                           │     │   │
│  │   │  · 生成定向改进指令                         │     │   │
│  │   └───────────┬───────────────────────────────┘     │   │
│  │               │                                      │   │
│  │   ┌───────────▼───────────────────────────────┐     │   │
│  │   │     THREE INDEPENDENT LAYERS               │     │   │
│  │   │                                            │     │   │
│  │   │  ┌─────────────┐  ← AGENT（多智能体研究）   │     │   │
│  │   │  │ EVIDENCE     │  · 多源并行检索           │     │   │
│  │   │  │ LAYER        │  · 证据规范化与分级        │     │   │
│  │   │  │              │  · 独立可测：覆盖率/新鲜度  │     │   │
│  │   │  └──────┬──────┘                           │     │   │
│  │   │         │                                   │     │   │
│  │   │  ┌──────▼──────┐  ← AGENT（推理与论证）     │     │   │
│  │   │  │ REASONING    │  · 大纲构建与故事线        │     │   │
│  │   │  │ LAYER        │  · Claim 生成与论证链      │     │   │
│  │   │  │              │  · 独立可测：一致性/覆盖面  │     │   │
│  │   │  └──────┬──────┘                           │     │   │
│  │   │         │                                   │     │   │
│  │   │  ┌──────▼──────┐  ← PIPELINE（确定性渲染）  │     │   │
│  │   │  │PRESENTATION  │  · 引用管理与脚注          │     │   │
│  │   │  │ LAYER        │  · 多格式渲染              │     │   │
│  │   │  │              │  · 独立可测：格式规范性     │     │   │
│  │   │  └─────────────┘                           │     │   │
│  │   └────────────────────────────────────────────┘     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                    PERSISTENCE LAYER                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐ │
│  │ IR Store    │  │ Evidence   │  │ Audit Log              │ │
│  │ (版本化)    │  │ Repository │  │ (token计量/决策记录)    │ │
│  └────────────┘  └────────────┘  └────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

**架构关键特性：**

**三层独立可测（Layer Independence）**：每一层有独立的输入/输出契约和评估指标。你可以在 Evidence Layer 不变的情况下改进 Reasoning Layer，也可以在两者都不变的情况下改进 Presentation Layer。这解决了 GPT v0.5 的"故障归因不可能"问题。

**认知循环（Cognitive Loop）**：Quality Oracle 不是事后检查站，而是持续运行的实时评估器。每完成一个 Claim 的证据收集或论证构建，Oracle 就评估该 Claim 的当前质量分。当某个维度不达标时，立即生成定向改进指令——例如"Claim #17 的证据覆盖率只有 0.5，需要额外检索来源 X 领域"。

**Loop Controller 做成本感知的停止决策**：它不只看质量分，还看每次迭代的边际收益。核心公式：

```
marginal_roi = (quality_score_after - quality_score_before) / tokens_consumed_this_iteration

if marginal_roi < threshold:
    if quality_score >= minimum_delivery_threshold:
        → DELIVER
    else:
        → REQUEST_HUMAN_DECISION（展示当前质量分 + 继续迭代的预估成本）
```

**Interactive Checkpoints**：用户可在三个关键节点介入：
- CP1（研究计划确认）：大纲 + 检索策略 + 预估成本 → 用户审批/修改
- CP2（证据审查）：关键证据的覆盖面 + 来源质量 → 用户确认是否充分
- CP3（初稿审查）：完整初稿 + 质量评分 → 用户决定交付/修改/深挖

---

## 2. 中间表示（Intermediate Representation, IR）

### 2.1 设计原则

IR 是整个系统的"唯一真相源"（Single Source of Truth）。所有格式的输出（PPT/PDF/Obsidian/Notion/Logseq/HTML）都从 IR 渲染生成，而不是独立撰写。

GPT v0.5 的 IR 设计方向正确，但缺少两个关键维度：**Claim 粒度分层**和**成本追踪字段**。

### 2.2 IR Schema（JSON，可直接落地）

```jsonc
{
  // ===== REPORT METADATA =====
  "report_id": "uuid",
  "version": "semver",  // e.g. "0.3.1"
  "parent_version": "semver | null",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",

  "spec": {
    "title": "string",
    "audience": "string",           // 目标读者画像
    "decision_context": "string",   // 读者要做什么决定
    "domain_profile": "academic | business | technical",
    "language": "string",
    "tone": "string",
    "target_length": {
      "executive_summary_pages": 2,
      "full_report_pages": 50,
      "ppt_slides": 25
    },
    "quality_target": 80,           // 0-100，目标质量分
    "token_budget": 5000000,        // 最大 token 消耗预算
    "deadline": "ISO8601 | null"
  },

  // ===== OUTLINE =====
  "outline": {
    "sections": [
      {
        "section_id": "string",
        "title": "string",
        "purpose": "string",        // 这一章要回答什么问题
        "section_type": "exec_summary | background | methodology | findings | analysis | recommendations | implementation | risks | appendix",
        "evidence_quota": 5,        // 本章至少需要多少条独立证据
        "children": []              // 递归子章节
      }
    ]
  },

  // ===== CLAIMS（双粒度） =====
  "claims": [
    {
      "claim_id": "string",
      "section_id": "string",       // 属于哪个章节
      "text": "string",             // 人类可读的断言文本

      // --- Claim 分类 ---
      "claim_type": "fact | inference | recommendation | definition",
      "importance": "critical | high | medium | low",
      // critical = ExecSummary/Recommendations/PPT标题
      // high = 正文关键结论
      // medium = 支撑性论述
      // low = 背景信息

      // --- 双粒度：Macro + Micro ---
      "micro_claims": [
        // 三元组级别，用于自动化验证
        {
          "micro_id": "string",
          "subject": "string",
          "predicate": "string",
          "object": "string",
          "temporal_scope": "string | null"  // e.g. "2025Q3", "as of 2025-12"
        }
      ],

      // --- 证据链接 ---
      "evidence_links": [
        {
          "evidence_id": "string",
          "relationship": "supports | refutes | provides_context | partially_supports",
          "support_span": "string",     // 来源中的具体支撑片段
          "span_locator": "string",     // 页码/段落/URL 锚点
          "verdict_confidence": 0.85    // 0-1，判定置信度
        }
      ],

      // --- 推理元数据 ---
      "assumptions": ["assumption_id"],  // 依赖的假设
      "confidence_level": "high | moderate | low | very_low",  // 借鉴 GRADE 四级
      "confidence_downgrade_reasons": [
        // GRADE 降级域
        "risk_of_bias | inconsistency | imprecision | indirectness | publication_bias"
      ],
      "counterarguments": [
        {
          "text": "string",
          "evidence_ids": ["string"],
          "rebuttal": "string | null"
        }
      ],

      // --- 状态追踪 ---
      "status": "draft | evidence_gathered | verified | disputed | final",
      "verification_history": [
        {
          "round": 1,
          "verifier_model": "claude-opus-4 | gpt-4.1 | ...",
          "verdict": "supported | refuted | nei",
          "timestamp": "ISO8601"
        }
      ]
    }
  ],

  // ===== EVIDENCE REPOSITORY =====
  "evidence": [
    {
      "evidence_id": "string",

      // --- 来源元数据 ---
      "url": "string",
      "title": "string",
      "author": "string | null",
      "publisher_root": "string",       // 机构级别，用于去重
      "root_domain": "string",
      "region": "string",               // 来源地区
      "source_type": "academic_journal | government | standard_body | company_filing | news_wire | industry_report | blog | social_media | database",
      "source_tier": 1,                 // 1=一手, 2=权威二手, 3=一般二手, 4=非正式

      // --- 时效性 ---
      "published_at": "ISO8601",
      "fetched_at": "ISO8601",
      "valid_until": "ISO8601 | null",  // 显式有效期
      "ttl_days": 30,                   // 默认 TTL（按领域配置）
      "is_time_sensitive": true,        // 是否包含可能快速变化的信息

      // --- 内容 ---
      "full_text_hash": "sha256",       // 用于检测内容变化
      "extracted_spans": [
        {
          "span_id": "string",
          "text": "string",
          "page_or_section": "string"
        }
      ]
    }
  ],

  // ===== ASSUMPTIONS REGISTRY =====
  "assumptions": [
    {
      "assumption_id": "string",
      "text": "string",
      "type": "scope | methodological | market | regulatory | technical",
      "sensitivity": "high | medium | low",  // 如果此假设不成立，影响多大
      "alternative_assumptions": ["string"],
      "dependent_claims": ["claim_id"]       // 哪些 Claim 依赖此假设
    }
  ],

  // ===== CONFLICT REGISTRY =====
  "conflicts": [
    {
      "conflict_id": "string",
      "claim_id": "string",
      "round": 1,
      "model_a": { "model": "string", "position": "string" },
      "model_b": { "model": "string", "position": "string" },
      "conflict_type": "factual | inferential | methodological | scope | terminological",
      "resolution": "accepted_a | accepted_b | merged | split_conditional | unresolved",
      "resolution_evidence": ["evidence_id"],
      "resolution_rationale": "string"
    }
  ],

  // ===== COST TRACKING =====
  "cost_ledger": {
    "total_tokens_consumed": 0,
    "total_estimated_cost_usd": 0.0,
    "by_layer": {
      "evidence": { "tokens": 0, "cost": 0.0 },
      "reasoning": { "tokens": 0, "cost": 0.0 },
      "presentation": { "tokens": 0, "cost": 0.0 },
      "quality_oracle": { "tokens": 0, "cost": 0.0 }
    },
    "by_iteration": [
      {
        "iteration": 1,
        "tokens": 0,
        "quality_before": 0,
        "quality_after": 0,
        "marginal_roi": 0.0
      }
    ]
  },

  // ===== FIGURES & DATA =====
  "figures": [
    {
      "figure_id": "string",
      "type": "chart | table | diagram | image",
      "title": "string",
      "data_source": "string",
      "claim_ids": ["string"],          // 此图支撑哪些 Claim
      "generation_method": "string"     // 代码/工具/手动
    }
  ],

  // ===== CHANGELOG =====
  "changelog": [
    {
      "version": "string",
      "timestamp": "ISO8601",
      "changes": "string",
      "triggered_by": "quality_oracle | human_feedback | conflict_resolution"
    }
  ]
}
```

### 2.3 IR 设计的关键决策解释

**为什么 Claim 需要双粒度（Macro + Micro）？**

Macro-Claim 是人类可读的段落级论述（例如"全球 AI 市场预计在 2030 年达到 5000 亿美元"）。Micro-Claim 是三元组级别的事实断言（例如 `{subject: "global AI market", predicate: "projected_value_2030", object: "$500B"}`）。

验证时用 Micro-Claim——自动化系统可以精确匹配三元组与证据中的具体数据。这一方向在 2025 年的 FactSelfCheck 论文中得到了验证：fact-level 粒度的幻觉检测比 sentence-level 的幻觉修正效果提升了 35.5%（对比 SelfCheckGPT 的 10.6%）。

呈现时用 Macro-Claim——人类读者不需要看三元组。

**为什么 Evidence 用 `publisher_root` 而不是 `domain`？**

同一机构的报告可能发布在多个域名上（例如 McKinsey 的报告可能在 mckinsey.com、LinkedIn、Medium 上都有）。用 `publisher_root`（机构级别）聚类，才能真正识别"独立来源"，防止转载刷分。

**为什么 Confidence Level 借鉴 GRADE 四级（而非连续值）？**

GRADE 框架被超过 110 个国际组织采用，经过 20+ 年验证。其核心洞见是：人类对"高/中/低/极低"四档的理解比对 "0.73 vs 0.71" 的连续数值更准确、更一致。但我们同时保留 `verdict_confidence` 连续值给自动化系统使用。

---

## 3. 多模型协作协议：动态角色对抗

### 3.1 为什么不用 GPT v0.5 的静态三角色

GPT v0.5 提出 Author-Critic-Verifier 三角色，并建议"Claude 做 Author，GPT 做 Critic"等固定分工。这有两个问题：

1. **角色固化导致盲区固化**：如果 GPT 总是做 Critic，它会形成固定的"找漏洞"模板——对某些类型的错误非常敏感，但对另一些类型系统性忽视
2. **最新研究表明混合方法最优**：2025 年底的统一框架研究证实，幻觉检测（内部一致性信号）和事实验证（外部证据信号）捕获的是互补的错误侧面，单独使用任何一种都不够

### 3.2 Meridian 协作协议：三回合交叉对抗

```
ROUND 1: PARALLEL INDEPENDENT DRAFTING
  Model A: 独立生成章节 X 的大纲 + 前 5 条关键 Claim
  Model B: 独立生成章节 X 的大纲 + 前 5 条关键 Claim
  → 输出：两份独立大纲 + 分歧点列表（Divergence Map）

ROUND 2: TARGETED DEEP DIVE ON DIVERGENCES
  对每个分歧点：
    - 两个模型各自提供支持其立场的证据
    - Quality Oracle 判定：哪个立场有更强的证据支持
    - 如果证据强度相当 → 记入 Conflict Registry，标注为条件性结论
  → 输出：合并后的大纲 + 已解决/未解决的分歧清单

ROUND 3: CROSS-VERIFICATION
  Model A 生成完整草稿
  Model B 对关键 Claim 抽样验证（不是审查写作质量，是验证事实准确性）：
    - 从证据中抽取 support span
    - 判定 Supported / Refuted / NEI
    - 检查同一报告内的数值一致性
  → 输出：验证报告 + 质量评分
```

**为什么 Round 1 是平行独立而非串行？**

因为这能发现"两个模型都不知道自己不知道的东西"。如果 Model A 写了一个结论但 Model B 完全没提到相关话题，这比"Model A 写了、Model B 审查后没挑出问题"更有信息量——后者可能只是 Model B 被 Model A 的措辞误导了。

**成本控制：不是每一章都需要三回合**

Loop Controller 负责决定哪些章节需要完整三回合对抗，哪些只需要单模型生成 + 自动化检查：

- **Critical Claims**（ExecSummary、Recommendations）→ 完整三回合
- **High importance Claims** → Round 1 + Round 3（跳过 Round 2 的深度分歧解决）
- **Medium/Low importance Claims** → 单模型生成 + 自动化一致性检查

---

## 4. 质量评分系统（Quality Oracle）

### 4.1 设计原则：反 Goodhart

所有评分指标必须同时通过两个检验：
1. **可靠计算检验**：用当前技术（2025 年 LLM + NLI 模型）能否可靠地自动计算？如果不能，标注为"半自动"并明确人工介入点
2. **反刷分检验**：如果系统优化这个指标，是否真的会提升报告质量？还是会导致"指标好看但实质下降"的 Goodhart 效应？

### 4.2 评分体系：三级架构

```
Level 1: HARD GATES（硬门禁，不过则不交付）
Level 2: QUANTITATIVE SCORE（量化分，0-100）
Level 3: CONFIDENCE META-SCORE（评分本身的可信度）
```

#### Level 1: Hard Gates（必须 100% 通过）

| Gate | 规则 | 自动化程度 |
|------|------|-----------|
| G1 | Critical Claim 零无源断言：ExecSummary / Recommendations / PPT 标题中的每个事实断言必须有 ≥1 条 evidence_link | 全自动 |
| G2 | 引用可回指：每条 evidence_link 必须包含非空的 support_span | 全自动 |
| G3 | 时效合规：时间敏感的 Critical Claim（is_time_sensitive=true）的所有证据必须在 valid_until 之前 | 全自动 |
| G4 | 内部数值一致：同一实体+同一指标在不同章节出现时，数值必须一致（或显式标注不同口径） | 半自动（自动检测候选对，人工确认） |

#### Level 2: Quantitative Score（100 分制）

**A. 证据质量（35 分）**

| 指标 | 分值 | 计算方式 | 阈值 | 自动化 | 反刷分机制 |
|------|------|---------|------|--------|-----------|
| A1 证据覆盖率 ECR | 10 | `#(Critical+High Claim 有≥1证据) / #(Critical+High Claim)` | ≥0.90 | 全自动 | 只计 Critical+High，防止用大量 Low Claim 稀释 |
| A2 独立来源支持率 CSR | 10 | `#(Critical Claim 有≥2个不同 publisher_root 的证据) / #(Critical Claim)` | ≥0.60 | 全自动 | 用 publisher_root 而非 URL 聚类 |
| A3 引用准确率（硬事实）CAR-H | 8 | 对含具体数字/日期/人名的 Micro-Claim，验证三元组与 support_span 的精确匹配 | ≥0.90 | 半自动（NLI + 规则匹配，低置信度的人工审查） | 只对可精确验证的硬事实计算，避免模糊判定 |
| A4 引用方向一致率 CAR-S | 4 | 对推断/趋势类 Claim，验证 support_span 与 Claim 的方向是否一致（正/负/中性） | ≥0.80 | 半自动 | 三分类（方向一致/方向相反/无关）比 FEVER 式蕴含判定更可靠 |
| A5 一手来源率 PSR | 3 | `#(Critical Claim 含≥1个 source_tier=1 的证据) / #(Critical Claim)` | ≥0.30 | 全自动 | — |

**为什么把 CAR 拆成 Hard 和 Soft？**

GPT v0.5 的 CAR≥0.95 要求用 FEVER 式蕴含判定来验证所有 Claim。但 FEVER 是闭域基准（Wikipedia），迁移到开放域（新闻、公司公告）时准确率显著下降。当前最好的开放域 NLI 模型 F1 在 0.7-0.85 之间——用一个 F1=0.8 的工具去要求 0.95 的准确率是逻辑矛盾。

拆分后：CAR-H 只对可精确验证的硬事实（数字、日期、专有名词）计算，这类匹配可以用规则+NLI 混合方法做到高准确率。CAR-S 对方向性判断用更宽松的三分类，更可靠。

**B. 来源多样性（8 分）**

| 指标 | 分值 | 计算方式 | 阈值 | 反刷分 |
|------|------|---------|------|--------|
| B1 有效来源数 ENS-P | 4 | `exp(H_publisher)`，其中 H 是基于 publisher_root 分布的 Shannon 熵。ENS 是"有效物种数"（Hill number of order 1） | ≥4 | Hill number 比 raw entropy 更直观：如果 ENS=4，意味着"等效于 4 个均匀分布的独立来源" |
| B2 来源类型覆盖 TC | 2 | `#(distinct source_type used) / #(source_type relevant to domain)` | ≥0.40 | 分母按领域调整（学术报告不需要 social_media） |
| B3 观点立场覆盖 SC | 2 | `#(Critical Claim 有≥1个不同立场的来源) / #(有争议的 Critical Claim)` | ≥0.50 | 只对标记为"有争议"的 Claim 计算 |

**为什么用有效来源数（ENS）而非 raw Shannon 熵？**

生态学家 Lou Jost（2006）的关键论证：Shannon 熵是对数尺度的，直觉上不可解释——H=2.0 并不意味着"2 个来源"。将其转换为 exp(H)（有效物种数 / Hill number of order 1）后，值的含义变成了"等效于 N 个均匀分布的独立来源"，直观且可比较。

GPT v0.5 建议用 Shannon 熵本身设阈值（≥0.65），这个数字没有直观含义。ENS≥4 的含义是清晰的：你的报告需要至少等效于 4 个独立来源的多样性。

**C. 逻辑与一致性（20 分）**

| 指标 | 分值 | 计算方式 | 阈值 | 自动化 |
|------|------|---------|------|--------|
| C1 定向一致性 TCC | 8 | 对"同实体+同指标"在不同章节的出现做自动配对，检查数值/方向一致性 | 矛盾对 ≤2 | 全自动（实体识别 + 数值比对），O(n) 而非 O(n²) |
| C2 不支持断言率 UCR | 8 | `#(Critical Claim 被任一 Verifier 判定为 NEI 或 Refuted) / #(Critical Claim)` | ≤0.05 | 半自动 |
| C3 不确定性标注率 UMR | 4 | `#(Inference/Recommendation 类 Claim 有 confidence_level 和 downgrade_reasons) / #(此类 Claim)` | ≥0.80 | 全自动 |

**为什么 C1 用"定向一致性检查"而非 GPT v0.5 的"全量矛盾对检测"？**

GPT v0.5 建议对所有 Claim 做图，用 NLI 检测所有可能的矛盾对。这在 200+ Claims 的报告中意味着 ~20,000 对的 NLI 判定，以当前 NLI 模型的 precision 水平，会产生大量假阳性。

Targeted Consistency Check 只检查"同一实体+同一指标"的跨章节出现（例如："全球 AI 市场"在第 2 章说"4000 亿"、在第 5 章说"5000 亿"）。这把 O(n²) 降到 O(n)，同时精准度大幅提高——因为配对条件已经极大缩小了候选集。

**D. 方法透明度（12 分）**

| 指标 | 分值 | 计算方式 | 阈值 |
|------|------|---------|------|
| D1 方法清单完备率 MCC | 6 | 8 项清单的完成比例（见下文） | ≥0.75 |
| D2 证据确定性标注率 ECC | 4 | `#(关键结论有 GRADE 式确定性等级 + 降级理由) / #(关键结论)` | ≥0.60 |
| D3 局限性覆盖 BLC | 2 | `#(章节有显式 Limitations 讨论) / #(实质性章节)` | ≥0.60 |

**D1 方法清单（8 项通用版）：**
1. 研究问题与范围边界的显式定义
2. 信息源与检索策略（关键词 / 数据库 / 时间范围）
3. 纳入/排除标准及其理由
4. 数据口径定义（字段、单位、统计方法）
5. 证据分级原则（source_tier 的定义规则）
6. 推断方法说明（模型、假设、计算逻辑）
7. 反例与替代解释的覆盖
8. 局限性与不确定性来源

**E. 可行动性（10 分）**

| 指标 | 分值 | 计算方式 | 阈值 |
|------|------|---------|------|
| E1 建议可执行度 ARS | 6 | `#(Recommendation 类 Claim 包含 owner/timeline/cost/risk/dependency 中≥3项) / #(Recommendation)` | ≥0.70 |
| E2 信息导航 NIS | 4 | 结构完备性评分：ToC + 交叉引用 + 关键结论索引 + 术语表（各 1 分） | ≥3/4 |

**F. 治理与审计（5 分）**

| 指标 | 分值 | 计算方式 | 阈值 |
|------|------|---------|------|
| F1 版本追踪 VTS | 2 | 所有输出物有 version + changelog | =1.00 |
| F2 分歧闭环率 CRS | 3 | `#(conflict status != 'unresolved') / #(conflicts)` | ≥0.70 |

**G. 成本效率（10 分）— GPT v0.5 完全遗漏**

| 指标 | 分值 | 计算方式 | 阈值 |
|------|------|---------|------|
| G1 质量密度 QD | 6 | `(A+B+C+D+E+F 分数) / (total_tokens / 1M)` | 按领域配置 |
| G2 收敛速度 CS | 4 | 达到 quality_target 所需的循环次数 | ≤5 |

**为什么增加成本效率维度？**

因为没有成本约束的质量追求是无意义的。一份花费 $500（~3000 万 tokens）达到 95 分的报告，在大多数商业场景下不如一份花费 $50 达到 82 分的报告有价值。G1 和 G2 强制系统在"质量提升"和"资源消耗"之间做显式权衡。

#### Level 3: Confidence Meta-Score（评分本身的可信度）

这解决 GPT v0.5 的 Critic 提出的"谁来验证 Verifier"问题。

| 指标 | 计算方式 | 阈值 |
|------|---------|------|
| Cross-Verification Agreement (CVA) | 对抽样 Critical Claims（≥20% 或 ≥30 条），两个模型独立做 Supported/Refuted/NEI 判定，计算一致率 | ≥0.80 |
| Canary Detection Rate (CDR) | 在证据库中注入 3-5 条已知错误的证据，检查 Verifier 是否检出 | ≥0.80 |
| Human Calibration Score (HCS) | 每季度在人工标注的校准集（~200 条）上评估 Verifier 准确率 | ≥0.85 |

**Canary Detection Rate 是关键创新**：它是对 Verifier 的实时"考试"。如果系统连已知错误都检不出来，所有验证结果都不可信。

### 4.3 评分函数：统一的连续化映射

所有比率指标用统一函数映射到分值（保留 GPT v0.5 的设计，但增加"反刷分权重"）：

```python
def score(value, weight, low, target, importance_weights=None):
    """
    value: 实际指标值
    weight: 该指标的满分分值
    low: 最低可接受值（低于此得 0 分）
    target: 目标值（达到此得满分）
    importance_weights: 如果指标是加权平均，传入权重
    """
    raw = clamp((value - low) / (target - low), 0.0, 1.0)
    return weight * raw

# 对"越低越好"的指标（如 UCR）：
def score_inverse(value, weight, target, worst):
    raw = clamp((worst - value) / (worst - target), 0.0, 1.0)
    return weight * raw
```

---

## 5. 多格式渲染系统

### 5.1 核心原则：IR → 渲染器，而非独立撰写

所有格式从同一份 IR 生成。渲染器不做内容决策，只做格式适配。

### 5.2 渲染器规格

| 格式 | 渲染逻辑 | 输出 | 适用场景 |
|------|---------|------|---------|
| **PDF** | IR → Quarto/LaTeX → PDF。完整报告含 ToC、脚注、参考文献、附录 | `.pdf` | 定稿交付、归档、审计 |
| **PPT** | 每个 Critical Claim → 1 页（Action Title + 关键图表 + 证据脚注）。备份页放 Medium Claims | `.pptx` | 汇报、评审、演示 |
| **Obsidian** | 每个 Claim → 1 个 .md 文件，用 `[[wikilinks]]` 连接。Evidence → 单独文件夹。YAML frontmatter 存元数据 | `.md` vault | 个人/团队知识沉淀 |
| **Logseq** | 每个 Claim → 1 个 block，用 `((block-ref))` 连接。Evidence 用 properties 标注 | `.md` (块格式) | 块级知识管理 |
| **Notion** | IR 映射到 Notion Block API。Claim → Toggle Block，Evidence → Database | API 调用 | 团队协作门户 |
| **Interactive HTML** | 可折叠章节、Claim 点击展开证据链、搜索、Claim 图谱可视化 | `.html` (single-file) | 最强交互体验 |
| **JSON** | IR 本身（去除内部状态字段） | `.json` | 程序化消费、API |

### 5.3 每个渲染物附带的溯源元数据

```jsonc
{
  "rendered_from_ir_version": "0.3.1",
  "rendered_at": "ISO8601",
  "claim_position_map": {
    // 渲染物中每个关键内容位置 → IR 中 Claim ID
    "slide_3_title": "claim_017",
    "page_12_paragraph_2": "claim_042"
  },
  "staleness_status": {
    // 渲染时计算：哪些底层证据已过期或接近过期
    "expired_evidence_count": 0,
    "expiring_within_7_days": 2,
    "affected_claims": ["claim_042"]
  }
}
```

---

## 6. Evidence Layer 的多智能体研究架构

### 6.1 借鉴 Anthropic 的 Orchestrator-Worker 模式

Anthropic 工程博客披露的多智能体研究系统架构是当前产业界的最佳实践。核心设计：

- **Lead Researcher**（强模型，如 Claude Opus 4）：分析查询、制定策略、分派子任务、综合结果
- **Sub-Agents**（高效模型，如 Claude Sonnet 4）：3-5 个并行执行具体检索任务
- **Citation Agent**：专门负责引用提取和来源验证

### 6.2 Meridian 的 Evidence Layer 实现

```
Lead Researcher（Claude Opus 4.6）
  │
  ├── SubAgent-1: 学术/论文检索（Sonnet 4.5）
  │     → 搜索学术数据库，提取结构化证据
  │
  ├── SubAgent-2: 新闻/公告检索（Sonnet 4.5）
  │     → 搜索新闻源、公司公告、政府文件
  │
  ├── SubAgent-3: 数据/统计检索（Sonnet 4.5）
  │     → 搜索数据库、报告中的具体数字
  │
  ├── SubAgent-4: 反方/争议检索（Sonnet 4.5）
  │     → 专门搜索反对意见、争议点、风险因素
  │
  └── Citation Verifier（Sonnet 4.5）
        → 对收集到的证据做初步的 span 提取和 tier 分级
```

**关键规则（来自 Anthropic 的工程经验）：**

1. **详细任务描述**：每个 SubAgent 需要明确的目标、输出格式、工具指引、任务边界。模糊指令会导致重复工作或遗漏。
2. **按复杂度缩放**：简单查询 → 1 个 SubAgent，3-10 次工具调用；中等复杂 → 2-4 个 SubAgent，各 10-15 次调用；高复杂 → 5+ SubAgent。
3. **SubAgent-4（反方检索）是 Meridian 的独特设计**：大多数研究系统只搜索支持性证据。专门设置一个"反方搜索者"确保报告不会系统性忽视反对意见。

---

## 7. 领域适配配置（Domain Profiles）

### 7.1 为什么一套评分卡不够

| 维度 | 学术报告 | 商业战略报告 | 技术文档 |
|------|---------|-------------|---------|
| 最核心质量 | 方法可复现 | 决策可行动 | 步骤可执行 |
| 引用标准 | 严格学术体例 | 咨询式脚注 | 版本号+链接 |
| "过时"定义 | 5年内算新 | 6个月内算新 | 上个版本后即过时 |
| 反方论证 | 必须 | 推荐 | 通常不需要 |
| 不确定性标注 | 必须 (GRADE) | 推荐 | 仅技术风险 |

### 7.2 Domain Profile Schema

```jsonc
{
  "profile_name": "business_strategy",

  // --- 评分权重覆盖 ---
  "score_weights": {
    "A_evidence": 30,       // 学术=40, 商业=30, 技术=25
    "B_diversity": 8,
    "C_consistency": 18,
    "D_methodology": 8,     // 学术=15, 商业=8, 技术=10
    "E_actionability": 16,  // 学术=5, 商业=16, 技术=15
    "F_governance": 5,
    "G_cost_efficiency": 15
  },

  // --- TTL 默认值 ---
  "default_ttl": {
    "market_data": 30,      // 天
    "policy_regulatory": 90,
    "technology_spec": 180,
    "academic_finding": 1825  // 5 年
  },

  // --- 来源类型权重 ---
  "preferred_source_types": [
    "company_filing", "industry_report", "government", "news_wire"
  ],

  // --- 必需章节 ---
  "required_sections": [
    "exec_summary", "background", "findings",
    "analysis", "recommendations", "implementation", "risks"
  ],

  // --- 可选章节 ---
  "optional_sections": [
    "methodology", "appendix"  // 学术报告中 methodology 是 required
  ]
}
```

---

## 8. 实施路线图

### Phase 1: Proof of Concept（2-3 周）

**目标**：验证核心循环——能否从"主题 → 带引用的 5 页报告"端到端运行

**范围**：
- Evidence Layer：单模型（非多智能体），Web 搜索 + 基本的 span 提取
- Reasoning Layer：大纲生成 + Claim 生成（不含双粒度 Micro-Claim）
- Presentation Layer：仅 Markdown 输出
- Quality Oracle：仅 Hard Gates（G1-G3）+ ECR + CSR
- 无多模型协作，单模型闭环

**验收标准**：
- 5 页报告，≥20 条 Claim，每条 Critical Claim 有 ≥1 evidence_link
- Hard Gates G1-G3 全部通过
- 端到端时间 < 10 分钟
- 总 token 消耗 < 50 万

### Phase 2: Quality Elevation（3-4 周）

**目标**：质量从"能看"到"可交付"

**新增**：
- Evidence Layer 升级为 Orchestrator-Worker 多智能体（1 Lead + 3 SubAgents）
- Reasoning Layer 增加双粒度 Claim（Macro + Micro）
- Quality Oracle 增加 CAR-H、C1（定向一致性）、D1（方法清单）
- 双模型协作：Round 1（平行独立）+ Round 3（交叉验证）
- Presentation Layer 增加 PDF + PPT

**验收标准**：
- 30 页报告，Level 2 总分 ≥ 70
- CAR-H ≥ 0.85
- CVA ≥ 0.75

### Phase 3: Production Readiness（4-6 周）

**目标**：完整系统上线

**新增**：
- 完整三回合对抗协议
- Quality Oracle 全量指标
- 所有格式渲染器
- Loop Controller 的成本感知停止决策
- Interactive Checkpoints
- Canary Detection
- Domain Profiles（至少 business + technical）
- 审计包输出

**验收标准**：
- 50 页报告，Level 2 总分 ≥ 80
- Level 3 CVA ≥ 0.80, CDR ≥ 0.80
- 成本效率 G1 达到领域配置的目标值

---

## 9. 交付物清单

最终系统生成的每份报告应包含两类交付物：

**面向读者：**
- 主报告（PDF / PPT / Notion / Obsidian / Logseq / HTML，按需求选择）
- Executive Summary（独立文件，2-5 分钟可读完）

**面向审计：**
- Evidence Table（每条 Critical Claim → 证据来源 + support_span + verdict）
- Methodology Log（检索策略 + 筛选规则 + 数据口径）
- Conflict Registry（双模型分歧点 + 解决方案）
- Quality Scorecard（Level 1 + Level 2 + Level 3 完整评分）
- Cost Report（token 消耗明细 + 每次迭代的边际收益率）
- Version History（IR 版本链 + changelog）

---

## 10. 与 Immortal Agent 的集成点

Meridian 的设计天然契合 Immortal Agent 的五层认知架构：

| Immortal Agent 层 | Meridian 对应 | 集成方式 |
|---|---|---|
| 数据捕获层 | Evidence Repository | 每份报告的结构化证据作为持久化知识资产入库 |
| 知识表示层 | IR (Claims + Evidence + Assumptions) | Claim 图谱可直接作为知识图谱的组成部分 |
| 推理层 | Reasoning Layer | 推理模式和论证链可复用于后续报告 |
| 记忆层 | Conflict Registry + Quality History | 历史分歧和质量趋势指导未来报告改进 |
| 进化层 | Domain Profiles + Calibration Set | 领域配置和校准集随使用持续优化 |

**关键集成设计**：每份报告生成后，Evidence Repository 中的高质量证据（source_tier ≤ 2, verdict = supported）应自动进入 Immortal Agent 的长期知识库，成为未来报告的可复用资产。这实现了"报告即知识积累"——每生成一份报告，系统就变得更聪明。
