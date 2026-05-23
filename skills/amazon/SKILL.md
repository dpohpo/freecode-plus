---
name: amazon
description: |
user-invocable: "true"
  Amazon ASIN Notion 报告生成器。搜索关键词，获取前10个ASIN，为每个ASIN生成独立的Notion风格HTML报告。

  使用场景：
  - 用户说 "/amazon 关键词" - 搜索并生成Notion风格报告
  - 用户说 "/amazon 关键词 -n 20" - 自定义ASIN数量
  - 用户说 "/amazon 关键词 -m jp" - 指定日本站点

  输出内容（每个ASIN一个HTML文件）：
  - ASIN号
  - 价格
  - 标题
  - Bullet Points（产品要点）
  - 首页Reviews（5条评论）

  输出位置：~/Desktop/amazon-notion/关键词/
  - index.html（索引页面）
  - B09XYZ1234.html（单个ASIN报告）
  - B08ABC5678.html
  - ...

  支持站点：美国(.com)、中国(.cn)、日本(.co.jp)、英国(.co.uk)、德国(.de)
---

# Amazon ASIN Notion 报告生成器

> **核心能力**: 搜索关键词 → 获取ASIN → 生成Notion风格HTML报告

## 快速使用

```bash
# 基本用法 - 获取前10个ASIN，每个生成一个Notion风格HTML报告
python3 ~/.claude/skills/amazon/scripts/amazon_notion_report.py "wireless hdmi"

# 自定义ASIN数量
python3 ~/.claude/skills/amazon/scripts/amazon_notion_report.py "wireless hdmi" -n 20

# 指定亚马逊站点（日本）
python3 ~/.claude/skills/amazon/scripts/amazon_notion_report.py "wireless hdmi" -m jp

# 自定义输出目录
python3 ~/.claude/skills/amazon/scripts/amazon_notion_report.py "wireless hdmi" -o ~/Desktop/my-reports
```

## 输出结构

```
~/Desktop/amazon-notion/wireless_hdmi/
├── index.html              # 索引页面（所有ASIN列表）
├── B09XYZ1234.html         # 第1个ASIN的报告
├── B08ABC5678.html         # 第2个ASIN的报告
├── B07DEF9012.html         # 第3个ASIN的报告
└── ...                     # 更多ASIN报告
```

## 每个报告包含

| 字段 | 说明 |
|------|------|
| ASIN | 亚马逊标准识别号 |
| 标题 | 商品完整标题 |
| 价格 | 当前价格 |
| 评分 | 星级评分（★★★★☆） |
| Bullet Points | 产品要点（最多5条） |
| 首页Reviews | 用户评论（最多5条） |
| 商品图片 | 主图展示 |
| Amazon链接 | 直接跳转购买 |

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `keyword` | 搜索关键词（必需） | - |
| `-n, --limit` | ASIN数量 | 10 |
| `-m, --marketplace` | 站点 (com/cn/jp/uk/de) | com |
| `-o, --output` | 输出目录 | ~/Desktop/amazon-notion |

## HTML报告样式

采用 Notion 设计风格：
- 📦 大图标标题区
- 📋 Callout 信息卡片
- ⭐ 星级评分显示
- 💬 评论卡片布局
- 🏷️ 标签系统
- 📱 响应式设计
- 🖨️ 支持打印

## 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: 爬取搜索结果（前三页）                               │
│  ↓                                                          │
│  Step 2: 获取每个商品详情（标题/价格/评分/Bullet Points）      │
│  ↓                                                          │
│  Step 3: 获取每个商品的差评（1-2星）                          │
│  ↓                                                          │
│  Step 4: 下载商品图片（ASIN命名）                            │
│  ↓                                                          │
│  Step 5: MECE 分析差评类别                                   │
│  ↓                                                          │
│  Step 6: Hardest 六维度极限推演                              │
│  ↓                                                          │
│  Step 7: 生成 DOCX 分析报告                                  │
└─────────────────────────────────────────────────────────────┘
```

## 快速使用

```bash
# ===== HTML导出模式（推荐 - Notion风格）=====
# 搜索关键词，获取前10个ASIN，每个ASIN生成一个独立的HTML文件
python3 scripts/amazon_html_exporter.py "wireless hdmi" -n 10

# 输出位置：~/Desktop/amazon-html/wireless_hdmi/
#   - B09XYZ1234.html    第一个ASIN的HTML文件
#   - B08ABC5678.html    第二个ASIN的HTML文件
#   - ...

# ===== 深度分析模式（MECE + Hardest）=====
# V2 反检测爬虫（推荐）
python3 scripts/amazon_crawler_v2.py "wireless hdmi" -p 3 -r 30

# V1 基础爬虫（可能被检测）
python3 scripts/amazon_crawler.py "wireless hdmi" -p 3 -r 30

# 分析数据 + 生成报告
python3 scripts/amazon_analyze.py "wireless hdmi"

# 输出位置：~/Desktop/amazon/
#   - products.csv / products.json    商品数据
#   - negative_reviews.csv/json       差评数据
#   - *.jpg                           商品图片（ASIN命名）
#   - analysis_report_*.docx          分析报告
```

---

## HTML 导出模式详细说明

> **新功能**: 为每个ASIN生成独立的Notion风格HTML文件

### 功能特点

- 🔍 搜索关键词，获取前N个ASIN
- 📝 每个ASIN生成一个独立HTML文件
- 🎨 Notion风格的精美设计
- 📦 包含：标题、价格、评分、Bullet Points、首页评论
- 🔗 包含Amazon商品链接

### 使用方法

```bash
# 基本用法（获取前10个ASIN）
python3 scripts/amazon_html_exporter.py "wireless hdmi"

# 自定义ASIN数量
python3 scripts/amazon_html_exporter.py "wireless hdmi" -n 20

# 指定亚马逊站点
python3 scripts/amazon_html_exporter.py "wireless hdmi" -m jp

# 自定义输出目录
python3 scripts/amazon_html_exporter.py "wireless hdmi" -o ~/Desktop/my-output
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `keyword` | 搜索关键词（必需） | - |
| `-n, --limit` | ASIN数量限制 | 10 |
| `-m, --marketplace` | 亚马逊站点 (com/cn/jp/uk/de) | com |
| `-o, --output` | 输出目录 | ~/Desktop/amazon-html |

### HTML文件结构

每个HTML文件包含以下内容：

```
┌─────────────────────────────────────┐
│ 面包屑导航 (Amazon > 关键词 > ASIN)    │
├─────────────────────────────────────┤
│ 商品标题                              │
│ ASIN徽章 | 品牌                       │
├─────────────────────────────────────┤
│ 商品主图                              │
├─────────────────────────────────────┤
│ 💰 价格                               │
├─────────────────────────────────────┤
│ ⭐ 评分 | 评论数                      │
├─────────────────────────────────────┤
│ 🛒 View on Amazon 链接              │
├─────────────────────────────────────┤
│ 📋 Product Features (Bullet Points) │
├─────────────────────────────────────┤
│ 💬 Customer Reviews                 │
│   - 评论卡片1                        │
│   - 评论卡片2                        │
│   - ...                             │
├─────────────────────────────────────┤
│ 标签 | #ASIN #关键词 #Amazon          │
└─────────────────────────────────────┘
```

---

## 参数说明

### amazon_crawler_v2.py（反检测爬虫 - 推荐）

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `keyword` | 搜索关键词（必需） | - |
| `-p, --pages` | 爬取页数 | 3 |
| `-r, --max-reviews` | 每商品最大差评数 | 30 |
| `-m, --marketplace` | 亚马逊站点 (com/cn/jp/uk/de) | com |
| `-o, --output` | 输出目录 | ~/Desktop/amazon |
| `--no-headless` | 显示浏览器窗口（调试用） | false |

### amazon_crawler.py（基础爬虫）

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `keyword` | 搜索关键词（必需） | - |
| `-p, --pages` | 爬取页数 | 3 |
| `-r, --max-reviews` | 每商品最大差评数 | 30 |
| `-m, --marketplace` | 亚马逊站点 (com/cn/jp/uk/de) | com |
| `-o, --output` | 输出目录 | ~/Desktop/amazon |

### amazon_analyze.py（分析）

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `keyword` | 关键词（用于报告标题） | - |
| `-d, --data-dir` | 数据目录 | ~/Desktop/amazon |
| `-o, --output` | 报告输出路径 | 自动生成 |
| `--no-docx` | 不生成DOCX | false |

## 数据字段

### 商品数据

| 字段 | 说明 |
|------|------|
| asin | 亚马逊标准识别号 |
| title | 商品标题 |
| brand | 品牌 |
| price | 价格 |
| rating | 评分（1-5） |
| review_count | 评论总数 |
| negative_review_count | 差评数量 |
| bullet_points | 要点列表 |
| bsr | Best Sellers Rank |
| image_url | 主图URL |
| url | 商品链接 |

### 差评数据

| 字段 | 说明 |
|------|------|
| asin | 商品ASIN |
| rating | 评分（1-2） |
| title | 评论标题 |
| body | 评论内容 |
| date | 评论日期 |
| verified | 是否验证购买 |
| helpful | 有用数 |

---

## MECE 差评分析框架

> 将差评拆解为**互斥穷尽**的类别

```
🧩 MECE 差评分类
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

├─ 产品质量问题    [高严重度]
│   ├─ 材质/做工缺陷
│   ├─ 耐用性差
│   └─ 与描述不符
│
├─ 功能/性能问题   [高严重度]
│   ├─ 连接不稳定
│   ├─ 信号/距离问题
│   └─ 画质/音质差
│
├─ 安装/使用问题   [中严重度]
│   ├─ 操作复杂
│   ├─ 说明书不清
│   └─ 配置困难
│
├─ 兼容性问题      [中严重度]
│   ├─ 设备不兼容
│   └─ 系统限制
│
├─ 物流/包装问题   [低严重度]
│   ├─ 运输损坏
│   └─ 配件缺失
│
├─ 价格/价值问题   [中严重度]
│   ├─ 性价比低
│   └─ 后悔购买
│
└─ 客服/售后问题   [中严重度]
    ├─ 响应慢
    └─ 退换困难
```

---

## Hardest 六维度极限推演

> Think deep, deeper, and deepest.

对每个关键差评类别进行六维度认知极限推演：

```
🧠 六维度认知极限推演
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────┐
│ 维度 ① 逻辑推理极限                    │
├─────────────────────────────────────┤
│ 根因分析：差评的真正原因是什么？         │
│ 证据链：从症状到根因的推理路径          │
│ 边界条件：什么情况下这个结论不成立？     │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 维度 ② 直觉洞察极限                    │
├─────────────────────────────────────┤
│ 第一直觉：用户真正想要什么？            │
│ 隐含假设：用户没有明说但期望的           │
│ 深层洞察：差评背后的情感需求            │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 维度 ③ 类比迁移极限                    │
├─────────────────────────────────────┤
│ 同类问题：竞品是否有相同问题？          │
│ 跨品类借鉴：其他品类如何解决类似问题？   │
│ 最佳实践：行业标杆是怎么做的？          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 维度 ④ 元认知审查极限                  │
├─────────────────────────────────────┤
│ 样本偏差：差评是否有代表性？            │
│ 情绪放大：用户是否因为愤怒而夸大？       │
│ 遗漏盲区：好评中是否隐含相同问题？       │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 维度 ⑤ 系统思维极限                    │
├─────────────────────────────────────┤
│ 上游因素：供应链/设计/品控哪个出问题？   │
│ 下游影响：问题会导致什么连锁反应？       │
│ 反馈循环：差评如何影响销量和排名？       │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 维度 ⑥ 第一性原理极限                  │
├─────────────────────────────────────┤
│ 核心需求：用户购买这类产品的本质需求？   │
│ 从零重建：如果不考虑现有方案，怎么解决？ │
│ 差异化机会：哪些需求没有被满足？         │
└─────────────────────────────────────┘
```

---

## DOCX 报告结构

```
# Amazon 商品深度分析报告

## 报告概要
- 分析关键词、时间、商品数、差评数

## 市场概览
- 平均评分、价格范围、样本数量

## MECE 差评分类分析
- 每个类别的差评数量、占比、严重度
- 典型差评示例

## Hardest 深度分析
- 六维度认知极限推演
- 每个痛点的深度分析

## 市场机会缺口
- 痛点 = 机会
- 差异化建议

## 商品数据汇总
- ASIN、标题、价格、评分、差评数表格

## 综合建议
- 按优先级排序的行动建议
```

---

## 注意事项

1. **反检测爬虫（V2）**：使用 undetected-chromedriver 实现真实浏览器环境
2. **请求频率**：内置随机延迟 + 人类行为模拟（滚动、点击）
3. **网络要求**：需要稳定网络，VPN 可能影响结果
4. **依赖安装**：
   ```bash
   # V2 反检测爬虫依赖
   pip3 install undetected-chromedriver --break-system-packages

   # V1 基础爬虫依赖
   pip3 install requests beautifulsoup4 --break-system-packages

   # 分析报告依赖
   pip3 install python-docx --break-system-packages
   ```
5. **数据时效**：亚马逊页面结构可能变化，脚本需更新适配

---

## 反检测技术说明（从 exotic-amazon 学习）

> 基于 PulsarRPA/exotic-amazon 项目的反爬策略优化

**核心问题**：
- requests 库缺少浏览器指纹，容易被识别
- selenium/playwright/puppeteer 会被检测出来
- headless 模式能够被检测
- 访问轨迹跟踪问题

**解决方案**：
1. **WebDriver 隐身**：使用 undetected-chromedriver
2. **人类行为模拟**：随机延迟、页面滚动、鼠标移动
3. **隐私上下文轮换**：每个任务独立会话
4. **RPA 交互**：点击"查看所有评论"、处理分页

---

## 铁律

1. **先爬后析**：必须先完成数据爬取再进行分析
2. **MECE不重不漏**：差评分类必须互斥且穷尽
3. **六维度全开**：高权重问题必须进行六维度分析
4. **深挖到底**：Think deep, deeper, deepest
5. **报告必输出**：分析完成后必须生成 DOCX 报告
