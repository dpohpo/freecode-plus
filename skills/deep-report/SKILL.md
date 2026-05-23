---
name: deep-report
description: |
user-invocable: "true"
  极致详尽报告生成系统 — 通过多AI协作（Claude + GPT左右互搏）生成顶级报告。

  核心特性：
  - 证据驱动：每个结论必须有权威来源支撑
  - 交叉验证：至少2个独立来源支持关键结论
  - 多格式输出：PPT/PDF/Obsidian/Notion/Logseq/HTML
  - 质量评分卡：可量化的报告质量指标
  - 左右互搏：Claude和GPT协作打磨到极致

  使用场景：
  - 用户说 "/deep-report 主题" - 生成极致详尽的报告
  - 用户说 "/deep-report 主题 --format notion" - 指定输出格式
  - 用户说 "/deep-report 主题 --mvp" - MVP模式（快速版）

license: MIT
---

# 极致详尽报告生成系统 (Deep Report Generator)

> **基于 Meridian 认知循环架构 + 设计美学规范**

---

## 设计元原则

在进入任何细节之前，先固定三条不可妥协的元原则：

**P1. 可追溯优先于详尽（Traceability > Exhaustiveness）**
一个只有 10 页但每个关键结论都能追溯到一手来源的报告，严格优于一个 100 页但引用模糊的报告。

**P2. 成本感知是一等公民（Cost-Awareness is First-Class）**
系统必须在每个决策点评估"边际质量提升 / 边际 token 成本"，在收益递减时主动停止。

**P3. 混合架构：确定性流水线 + 智能体**
用确定性流水线处理格式渲染、引用管理，用智能体处理信息检索、证据评估。

---

## 总体架构：认知循环（Cognitive Loop）

```
┌──────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                       │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │ Checkpoint 1 │  │ Checkpoint 2 │  │ Checkpoint 3         │ │
│  │ 研究计划确认  │  │ 证据审查     │  │ 初稿审查 / 交付决策   │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬───────────┘ │
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
│  │   └───────────────────────────────────────────┘     │   │
│  │                                                      │   │
│  │   ┌───────────────────────────────────────────┐     │   │
│  │   │         QUALITY ORACLE                     │     │   │
│  │   │  · 实时评分（不是事后检查）                   │     │   │
│  │   │  · 定位最薄弱维度                           │     │   │
│  │   │  · 生成定向改进指令                         │     │   │
│  │   └───────────────────────────────────────────┘     │   │
│  │                                                      │   │
│  │   ┌───────────────────────────────────────────┐     │   │
│  │   │     THREE INDEPENDENT LAYERS               │     │   │
│  │   │                                            │     │   │
│  │   │  ┌─────────────┐  ← AGENT（多智能体研究）   │     │   │
│  │   │  │ EVIDENCE     │  · 多源并行检索           │     │   │
│  │   │  │ LAYER        │  · 证据规范化与分级        │     │   │
│  │   │  └──────┬──────┘                           │     │   │
│  │   │         │                                   │     │   │
│  │   │  ┌──────▼──────┐  ← AGENT（推理与论证）     │     │   │
│  │   │  │ REASONING    │  · 大纲构建与故事线        │     │   │
│  │   │  │ LAYER        │  · Claim 生成与论证链      │     │   │
│  │   │  └──────┬──────┘                           │     │   │
│  │   │         │                                   │     │   │
│  │   │  ┌──────▼──────┐  ← PIPELINE（确定性渲染）  │     │   │
│  │   │  │PRESENTATION  │  · 引用管理与脚注          │     │   │
│  │   │  │ LAYER        │  · 多格式渲染              │     │   │
│  │   │  └─────────────┘                           │     │   │
│  │   └────────────────────────────────────────────┘     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              PERSISTENCE LAYER                        │   │
│  │  IR Store  │  Evidence Repository  │  Audit Log       │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

---

## 中间表示（IR Schema）

IR 是整个系统的"唯一真相源"。所有格式的输出都从 IR 渲染生成。

```typescript
interface ReportIR {
  // 元数据
  report_id: string;
  version: string;
  created_at: string;
  updated_at: string;

  // 规格说明
  spec: {
    title: string;
    audience: string;
    decision_context: string;
    domain_profile: 'academic' | 'business' | 'technical';
    quality_target: number;      // 0-100
    token_budget: number;
    deadline?: string;
  };

  // 大纲结构
  outline: {
    sections: SectionNode[];
  };

  // 核心断言（双粒度）
  claims: Claim[];

  // 证据池
  evidence: Evidence[];

  // 假设注册表
  assumptions: Assumption[];

  // 冲突注册表
  conflicts: Conflict[];

  // 成本追踪
  cost_ledger: CostLedger;
}

// Claim 双粒度设计
interface Claim {
  claim_id: string;
  section_id: string;
  text: string;                    // Macro-Claim：人类可读

  claim_type: 'fact' | 'inference' | 'recommendation' | 'definition';
  importance: 'critical' | 'high' | 'medium' | 'low';

  // Micro-Claims：三元组级别，用于自动化验证
  micro_claims: {
    micro_id: string;
    subject: string;
    predicate: string;
    object: string;
    temporal_scope?: string;
  }[];

  // 证据链接
  evidence_links: {
    evidence_id: string;
    relationship: 'supports' | 'refutes' | 'provides_context' | 'partially_supports';
    support_span: string;        // 来源中的具体支撑片段
    span_locator: string;        // 页码/段落/URL 锚点
    verdict_confidence: number;  // 0-1
  }[];

  // 置信度（GRADE 四级）
  confidence_level: 'high' | 'moderate' | 'low' | 'very_low';
  confidence_downgrade_reasons: string[];

  // 反方论点
  counterarguments: {
    text: string;
    evidence_ids: string[];
    rebuttal?: string;
  }[];

  status: 'draft' | 'evidence_gathered' | 'verified' | 'disputed' | 'final';
}

// 证据结构
interface Evidence {
  evidence_id: string;
  url: string;
  title: string;
  author?: string;
  publisher_root: string;         // 机构级别，用于去重
  source_type: 'academic_journal' | 'government' | 'standard_body' | 'company_filing' | 'news_wire' | 'industry_report' | 'blog' | 'database';
  source_tier: 1 | 2 | 3 | 4;     // 1=一手, 2=权威二手, 3=一般二手, 4=非正式

  published_at: string;
  fetched_at: string;
  valid_until?: string;
  is_time_sensitive: boolean;

  extracted_spans: {
    span_id: string;
    text: string;
    page_or_section: string;
  }[];
}

// 冲突注册表
interface Conflict {
  conflict_id: string;
  claim_id: string;
  model_a: { model: string; position: string };
  model_b: { model: string; position: string };
  conflict_type: 'factual' | 'inferential' | 'methodological' | 'scope';
  resolution: 'accepted_a' | 'accepted_b' | 'merged' | 'unresolved';
  resolution_rationale: string;
}

// 成本追踪
interface CostLedger {
  total_tokens_consumed: number;
  total_estimated_cost_usd: number;
  by_iteration: {
    iteration: number;
    tokens: number;
    quality_before: number;
    quality_after: number;
    marginal_roi: number;
  }[];
}
```

---

## 多模型协作协议：三回合交叉对抗

```
ROUND 1: PARALLEL INDEPENDENT DRAFTING
  Model A: 独立生成章节 X 的大纲 + 前 5 条关键 Claim
  Model B: 独立生成章节 X 的大纲 + 前 5 条关键 Claim
  → 输出：两份独立大纲 + 分歧点列表（Divergence Map）

ROUND 2: TARGETED DEEP DIVE ON DIVERGENCES
  对每个分歧点：
    - 两个模型各自提供支持其立场的证据
    - Quality Oracle 判定：哪个立场有更强的证据支持
    - 如果证据强度相当 → 记入 Conflict Registry
  → 输出：合并后的大纲 + 已解决/未解决的分歧清单

ROUND 3: CROSS-VERIFICATION
  Model A 生成完整草稿
  Model B 对关键 Claim 抽样验证：
    - 从证据中抽取 support span
    - 判定 Supported / Refuted / NEI
    - 检查同一报告内的数值一致性
  → 输出：验证报告 + 质量评分
```

**成本控制：按 Claim 重要性分级**

- **Critical Claims**（ExecSummary、Recommendations）→ 完整三回合
- **High importance Claims** → Round 1 + Round 3
- **Medium/Low importance Claims** → 单模型生成 + 自动化一致性检查

---

## 质量评分系统（Quality Oracle）

### 三级架构

```
Level 1: HARD GATES（硬门禁，不过则不交付）
Level 2: QUANTITATIVE SCORE（量化分，0-100）
Level 3: CONFIDENCE META-SCORE（评分本身的可信度）
```

### Level 1: Hard Gates（必须 100% 通过）

| Gate | 规则 | 自动化 |
|------|------|--------|
| G1 | Critical Claim 零无源断言：每个事实断言必须有 ≥1 条 evidence_link | 全自动 |
| G2 | 引用可回指：每条 evidence_link 必须包含非空的 support_span | 全自动 |
| G3 | 时效合规：时间敏感 Critical Claim 的所有证据必须在 valid_until 之前 | 全自动 |
| G4 | 内部数值一致：同一实体+同一指标在不同章节出现时，数值必须一致 | 半自动 |

### Level 2: Quantitative Score（100 分制）

**A. 证据质量（35 分）**

| 指标 | 分值 | 计算方式 | 阈值 |
|------|------|---------|------|
| A1 证据覆盖率 ECR | 10 | Critical+High Claim 有≥1证据的比例 | ≥0.90 |
| A2 独立来源支持率 CSR | 10 | Critical Claim 有≥2个不同 publisher_root 证据的比例 | ≥0.60 |
| A3 引用准确率（硬事实）CAR-H | 8 | 含具体数字/日期的 Micro-Claim 精确匹配率 | ≥0.90 |
| A4 引用方向一致率 CAR-S | 4 | 推断类 Claim 方向一致性（正/负/中性） | ≥0.80 |
| A5 一手来源率 PSR | 3 | Critical Claim 含 source_tier=1 证据的比例 | ≥0.30 |

**B. 来源多样性（8 分）**

| 指标 | 分值 | 计算方式 | 阈值 |
|------|------|---------|------|
| B1 有效来源数 ENS-P | 4 | exp(H_publisher)，Shannon 熵的有效物种数 | ≥4 |
| B2 来源类型覆盖 TC | 2 | 使用的 source_type 种类 / 领域相关类型 | ≥0.40 |
| B3 观点立场覆盖 SC | 2 | 有争议 Claim 有不同立场来源的比例 | ≥0.50 |

**C. 逻辑与一致性（20 分）**

| 指标 | 分值 | 计算方式 | 阈值 |
|------|------|---------|------|
| C1 定向一致性 TCC | 8 | 同实体+同指标跨章节数值一致性 | 矛盾对 ≤2 |
| C2 不支持断言率 UCR | 8 | Critical Claim 被 Verifier 判定为 NEI/Refuted 比例 | ≤0.05 |
| C3 不确定性标注率 UMR | 4 | Inference/Recommendation 有 confidence_level 的比例 | ≥0.80 |

**D. 方法透明度（12 分）**

| 指标 | 分值 | 计算方式 | 阈值 |
|------|------|---------|------|
| D1 方法清单完备率 MCC | 6 | 8 项清单完成比例 | ≥0.75 |
| D2 证据确定性标注率 ECC | 4 | 关键结论有 GRADE 等级+降级理由比例 | ≥0.60 |
| D3 局限性覆盖 BLC | 2 | 章节有显式 Limitations 讨论比例 | ≥0.60 |

**D1 方法清单（8 项）**：
1. 研究问题与范围边界的显式定义
2. 信息源与检索策略
3. 纳入/排除标准及其理由
4. 数据口径定义
5. 证据分级原则
6. 推断方法说明
7. 反例与替代解释的覆盖
8. 局限性与不确定性来源

**E. 可行动性（10 分）**

| 指标 | 分值 | 计算方式 | 阈值 |
|------|------|---------|------|
| E1 建议可执行度 ARS | 6 | Recommendation 包含 owner/timeline/cost/risk/dependency ≥3项 | ≥0.70 |
| E2 信息导航 NIS | 4 | ToC + 交叉引用 + 关键结论索引 + 术语表 | ≥3/4 |

**F. 治理与审计（5 分）**

| 指标 | 分值 | 计算方式 | 阈值 |
|------|------|---------|------|
| F1 版本追踪 VTS | 2 | 所有输出物有 version + changelog | =1.00 |
| F2 分歧闭环率 CRS | 3 | conflict status != 'unresolved' 比例 | ≥0.70 |

**G. 成本效率（10 分）**

| 指标 | 分值 | 计算方式 | 阈值 |
|------|------|---------|------|
| G1 质量密度 QD | 6 | (A+B+C+D+E+F 分数) / (total_tokens / 1M) | 按领域配置 |
| G2 收敛速度 CS | 4 | 达到 quality_target 所需的循环次数 | ≤5 |

### Level 3: Confidence Meta-Score

| 指标 | 计算方式 | 阈值 |
|------|---------|------|
| Cross-Verification Agreement (CVA) | 两模型独立判定 Supported/Refuted/NEI 一致率 | ≥0.80 |
| Canary Detection Rate (CDR) | 注入已知错误证据的检出率 | ≥0.80 |

### 质量等级

- 90-100: 卓越 (Exceptional)
- 80-89: 优秀 (Excellent)
- 70-79: 合格 (Pass)
- 60-69: 需改进 (Needs Work)
- <60: 不合格 (Fail)

---

## 多格式渲染系统

| 格式 | 渲染逻辑 | 适用场景 |
|------|---------|---------|
| **PDF** | IR → Quarto/LaTeX → PDF | 定稿交付、归档、审计 |
| **PPT** | 每个 Critical Claim → 1 页 | 汇报、评审、演示 |
| **Obsidian** | 每个 Claim → 1 个 .md 文件，wikilinks 连接 | 个人/团队知识沉淀 |
| **Logseq** | 每个 Claim → 1 个 block | 块级知识管理 |
| **Notion** | IR 映射到 Notion Block API | 团队协作门户 |
| **Interactive HTML** | 可折叠章节、Claim 点击展开证据链 | 最强交互体验 |
| **JSON** | IR 本身（去除内部状态字段） | 程序化消费、API |

---

## 交付物清单

**面向读者：**
- 主报告（PDF / PPT / Notion / Obsidian / HTML，按需求选择）
- Executive Summary（独立文件，2-5 分钟可读完）

**面向审计：**
- Evidence Table（每条 Critical Claim → 证据来源 + support_span + verdict）
- Methodology Log（检索策略 + 筛选规则 + 数据口径）
- Conflict Registry（双模型分歧点 + 解决方案）
- Quality Scorecard（Level 1 + Level 2 + Level 3 完整评分）
- Cost Report（token 消耗明细 + 每次迭代的边际收益率）
- Version History（IR 版本链 + changelog）

---

## 🎨 设计美学规范（Visual Design System）

> 基于 BHT 极限认知推演 + 顶级咨询公司设计最佳实践

### 核心设计哲学

```
┌─────────────────────────────────────────────────────────────┐
│                    设计金字塔                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│    层级 1：功能 > 形式（Function over Form）                  │
│    ├── 设计服务于信息传达，而非装饰                           │
│    └── 每个像素都有明确目的                                   │
│                                                             │
│    层级 2：克制 > 花哨（Restraint over Flash）               │
│    ├── 顶级设计 = 有意的删减                                 │
│    └── 删到不能再删，就是最好的设计                           │
│                                                             │
│    层级 3：一致性 > 创意（Consistency over Creativity）       │
│    ├── 读者不应在每个页面重新学习设计语言                      │
│    └── 可预测 = 可信任                                       │
│                                                             │
│    层级 4：呼吸感 > 信息密度（Breathing Room > Density）      │
│    ├── 留白不是浪费，是认知缓冲                               │
│    └── 信息密度越高，越需要空间                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 视觉层次系统

| 手段 | Level 1（最高） | Level 2（中等） | Level 3（最低） |
|------|----------------|----------------|----------------|
| 字号 | 24-32pt | 14-18pt | 10-12pt |
| 字重 | Bold (700) | Medium (500) | Regular (400) |
| 颜色 | 主色/黑色 | 深灰色 (#333) | 浅灰色 (#666) |
| 位置 | 顶部/居中 | 中间区域 | 底部/侧边 |

---

### 排版系统 (Typography)

```
字体选择：
├── 标题字体：Inter / SF Pro Display / Noto Sans SC
├── 正文字体：Inter / SF Pro Text / Noto Sans SC
├── 代码字体：JetBrains Mono / Fira Code
└── 限定：最多 2 个字体族

字号阶梯（1.25× 增长比例）：
├── H1: 32px (2rem)     ← 报告标题
├── H2: 25.6px (1.6rem) ← 章节标题
├── H3: 20.5px (1.28rem)← 小节标题
├── Body: 16px (1rem)   ← 正文
├── Caption: 12.8px     ← 图注/脚注
└── Code: 14px          ← 代码块

间距系统（8px 基准网格）：
├── 行高：1.6 × 字号
├── 段落间距：1.5em（24px）
├── 章节间距：3em（48px）
└── 列表缩进：1.5em

每行字符数：
├── 英文最优：60-75 字符
├── 中文最优：35-40 字符
```

---

### 色彩系统 (Color System)

```
主色（Primary）- 专业、信任
├── 专业蓝：#0066CC
├── 深邃黑：#1A1A1A
└── 用途：标题、强调、CTA按钮、图表主色

语义色（Semantic）- 信息分类
├── ✅ 成功/机会：#10B981（绿）
├── ⚠️ 警告/注意：#F59E0B（橙）
├── ❌ 错误/风险：#EF4444（红）
├── ℹ️ 信息/中性：#3B82F6（蓝）
└── 💡 洞察/建议：#8B5CF6（紫）

中性色（Neutral）- 层次与可读性
├── 标题文字：#111827
├── 正文文字：#374151
├── 次要文字：#6B7280
├── 边框线条：#E5E7EB
└── 背景底色：#F9FAFB

60-30-10 配色法则：
├── 60% 中性色（背景、正文）
├── 30% 辅助色（图表、强调）
└── 10% 主色（关键 CTA、焦点）

无障碍要求：对比度 ≥ 4.5:1（WCAG AA 标准）
```

---

### 留白系统 (White Space)

```
留白比例建议：
├── 极简风格：40-50% 留白
├── 专业风格：30-40% 留白
└── 信息密集：20-30% 留白

页面边距规范：
├── 顶部：64px
├── 左右边距：48px
├── 章节间距：32-48px
└── 底部：64px
```

---

### 数据可视化 (Data Visualization)

```
图表选择决策树：

你想展示什么？
│
├── 比较 (Comparison)
│   ├── 类别少 → 柱状图 (Bar Chart)
│   └── 类别多 → 分组柱状图 (Grouped Bar)
│
├── 趋势 (Trend)
│   ├── 连续时间 → 折线图 (Line Chart)
│   └── 累积效果 → 面积图 (Area Chart)
│
├── 占比 (Composition)
│   ├── 少量部分 → 环形图 (Donut Chart)
│   └── 层级结构 → 树状图 (Treemap)
│
├── 关系 (Relationship)
│   ├── 两变量 → 散点图 (Scatter Plot)
│   └── 多变量 → 气泡图 (Bubble Chart)
│
└── 流程 (Flow)
    ├── 线性流程 → 漏斗图 (Funnel)
    └── 流向转移 → 桑基图 (Sankey)

图表设计铁律：
├── 去掉图表垃圾：3D效果、多余网格线、装饰性元素
├── 数据墨水比最大化：每滴墨水都要传达信息
├── 标题即结论：「销售额增长50%」而非「销售额趋势」
├── 标注关键点：峰值、谷值、转折点
└── 统一配色：与报告整体色彩系统一致
```

---

### 组件库 (Component Library)

#### Callout 高亮块

```markdown
> 🎯 **核心结论**
> 这是关键结论的详细说明

> ⚠️ **风险提示**
> 需要注意的事项

> 💡 **洞察发现**
> 反直觉的发现或建议
```

#### 表格样式

```markdown
| 指标 | 当前值 | 目标值 | 差距 | 状态 |
|------|--------|--------|------|------|
| 指标A | 100 | 120 | +20% | ✅ 达标 |
| 指标B | 80 | 100 | -20% | ⚠️ 需改进 |
```

**表格设计规范**：
- 表头：加粗、深色背景 (#F3F4F6)
- 斑马纹：偶数行浅灰 (#F9FAFB)
- 对齐：数字右对齐，文本左对齐
- 状态列：使用 emoji + 颜色编码

---

### 平台特定设计规范

#### 📄 PDF 输出

```
页面设置：
├── 尺寸：A4 (210×297mm) 或 Letter (8.5×11in)
├── 页边距：上下 25mm，左右 20mm
└── 分栏：单栏为主，数据密集区可双栏

页眉页脚：
├── 页眉：报告标题（左） | 章节名（右）
├── 页脚：页码（居中） | 日期（右）
└── 分隔线：0.5pt 灰色线条
```

#### 📊 PPT 输出

```
幻灯片设置：
├── 比例：16:9 (1920×1080px)
├── 安全区：距边缘 50px
└── 网格：12列网格系统

Action Title 法则：
├── 标题是完整的结论句
├── 不用「...概览」「...分析」
└── 示例：「市场份额增长25%，主要由亚太区驱动」

6×6 法则：
├── 每页最多 6 个要点
└── 每个要点最多 6 个词
```

#### 📝 Notion 输出

```
Notion 特有组件：
├── Callout：关键结论高亮（带 emoji）
├── Toggle：详细内容折叠
├── 数据库：Claims / Evidence / Actions 表格
├── 分栏：利用多列布局
└── 目录：/table-of-contents 命令

Callout 类型对照：
├── 🎯 核心结论 → 蓝色背景
├── ⚠️ 风险警告 → 黄色背景
├── ✅ 最佳实践 → 绿色背景
└── 💡 洞察建议 → 紫色背景
```

#### 🔮 Obsidian 输出

```
Obsidian 特有语法：
├── Wikilinks：[[内部链接]] 建立知识网络
├── 标签：#claim #evidence #recommendation
├── 嵌入：![[image.png]] 嵌入资源
└── Callout：> [!note] 标准语法

文件组织：
├── 主报告.md（主文件）
├── claims/（断言卡片）
├── evidence/（证据卡片）
└── attachments/（图片附件）
```

---

### 设计检查清单

```
□ 视觉层次
  □ 标题明显大于正文
  □ 重要信息位置突出
  □ 色彩编码一致

□ 排版
  □ 字体种类 ≤ 2
  □ 行高 1.5-1.7
  □ 每行字符数在合理范围

□ 留白
  □ 章节间有明显间距
  □ 页边距充足
  □ 内容不拥挤

□ 色彩
  □ 主色使用克制（≤10%）
  □ 语义色含义一致
  □ 对比度满足无障碍要求

□ 数据可视化
  □ 图表类型选择正确
  □ 无图表垃圾
  □ 标题即结论
```

---

## 使用示例

```bash
# 基本用法
/deep-report "AI Agent市场分析报告"

# 指定格式
/deep-report "AI Agent市场分析报告" --format notion

# MVP模式（快速版）
/deep-report "AI Agent市场分析报告" --mvp

# 完整模式（包含三回合对抗）
/deep-report "AI Agent市场分析报告" --full-debate

# 指定质量门槛
/deep-report "AI Agent市场分析报告" --min-score 85
```

---

## 铁律

### 内容质量铁律

1. **[HARD] 证据先行** - 没有证据不许下结论
2. **[HARD] 交叉验证** - 关键结论至少2个独立来源
3. **[HARD] 不确定性标注** - 所有推断必须标明置信度
4. **[HARD] 来源分级** - 一手>二手>三手
5. **[HARD] 逻辑一致性** - 章节间不许矛盾
6. **[HARD] 质量门槛** - Level 2 评分<70不许交付
7. **[HARD] 成本感知** - 边际收益率低于阈值时停止迭代

### 设计美学铁律

8. **[HARD] 功能优先** - 设计服务于信息传达，禁止纯装饰性元素
9. **[HARD] 克制原则** - 最多2种字体、3种颜色（不含中性色）
10. **[HARD] 留白必须** - 页面留白≥20%，专业报告≥30%
11. **[HARD] 层次清晰** - 通过字号/字重/颜色区分，禁止全篇同一字号
12. **[HARD] 图表纯净** - 禁止3D效果、无意义装饰、多余网格线
13. **[HARD] 一致性** - 同类元素必须样式相同
14. **[HARD] 无障碍** - 对比度≥4.5:1（WCAG AA）

---

## 模板：默认报告结构

```markdown
# [报告标题]

> **版本**: v1.0 | **日期**: YYYY-MM-DD | **质量评分**: XX/100

## Executive Summary
- 核心结论 1 [^1]
- 核心结论 2 [^2]
- 核心结论 3 [^3]

## 1. 背景与定义
### 1.1 问题定义
### 1.2 研究范围
### 1.3 关键假设

## 2. 研究方法
### 2.1 检索策略
### 2.2 筛选标准
### 2.3 证据分级原则

## 3. 核心发现
### 3.1 发现A
### 3.2 发现B
### 3.3 发现C

## 4. 深度分析
### 4.1 驱动因素分析
### 4.2 敏感性分析
### 4.3 情景模拟

## 5. 建议与行动
### 5.1 选项对比
### 5.2 推荐方案
### 5.3 行动计划

## 6. 风险与限制
### 6.1 风险矩阵
### 6.2 研究局限

---

## 附录
### Appendix A: 证据表（Evidence Table）
### Appendix B: 冲突注册表（Conflict Registry）
### Appendix C: 质量评分卡（Quality Scorecard）
### Appendix D: 成本报告（Cost Report）
```

---

> **报告的本质不是文字——是可追溯的决策支撑链。**
