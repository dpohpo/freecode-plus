# HTML Interactive Report Generator

> **生成专业交互式HTML报告的技能包**
>
> 核心能力：数据可视化、响应式设计、交互式组件、排版层级系统

---

## 技能概述

生成专业级交互式HTML报告，支持动态图表、滚动叙事、实时数据更新和跨设备响应式布局。

**适用场景**：
- 数据分析报告
- 商业仪表盘
- 年度/季度报告
- 研究报告展示
- 交互式数据故事

---

## 核心设计原则

### 1. 排版层级系统（Typographic Hierarchy）

```css
/* 字体系统 - 最多2-3种字体 */
:root {
  --font-heading: 'Inter', 'SF Pro Display', system-ui, sans-serif;
  --font-body: 'SF Pro Text', -apple-system, sans-serif;
  --font-mono: 'SF Mono', 'JetBrains Mono', monospace;

  /* 字号层级 */
  --text-xs: 0.75rem;   /* 12px - 注释/标注 */
  --text-sm: 0.875rem;  /* 14px - 小标题/说明 */
  --text-base: 1rem;    /* 16px - 正文 */
  --text-lg: 1.125rem;  /* 18px - 强调文本 */
  --text-xl: 1.25rem;   /* 20px - 小节标题 */
  --text-2xl: 1.5rem;   /* 24px - 节标题 */
  --text-3xl: 1.875rem; /* 30px - 页面标题 */
  --text-4xl: 2.25rem;  /* 36px - 主标题 */

  /* 字重 */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* 行高 */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;

  /* 间距系统 - 8px基准 */
  --space-1: 0.25rem;  /* 4px */
  --space-2: 0.5rem;   /* 8px */
  --space-3: 0.75rem;  /* 12px */
  --space-4: 1rem;     /* 16px */
  --space-5: 1.25rem;  /* 20px */
  --space-6: 1.5rem;   /* 24px */
  --space-8: 2rem;     /* 32px */
  --space-10: 2.5rem;  /* 40px */
  --space-12: 3rem;    /* 48px */
  --space-16: 4rem;    /* 64px */
}
```

### 2. 配色系统（Color System）

```css
:root {
  /* 主色调 - 可自定义 */
  --color-primary: #2563eb;
  --color-primary-light: #3b82f6;
  --color-primary-dark: #1d4ed8;

  /* 中性色 */
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-300: #d1d5db;
  --color-gray-400: #9ca3af;
  --color-gray-500: #6b7280;
  --color-gray-600: #4b5563;
  --color-gray-700: #374151;
  --color-gray-800: #1f2937;
  --color-gray-900: #111827;

  /* 语义色 */
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;

  /* 背景色 */
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  --bg-tertiary: #f3f4f6;

  /* 文字色 */
  --text-primary: #111827;
  --text-secondary: #6b7280;
  --text-tertiary: #9ca3af;

  /* 边框色 */
  --border-color: #e5e7eb;
  --border-color-light: #f3f4f6;
}
```

### 3. 响应式断点（Responsive Breakpoints）

```css
/* 移动优先断点 */
/* 小于 640px - 移动端（默认） */
/* 640px - 768px - 平板竖屏 */
/* 768px - 1024px - 平板横屏 */
/* 1024px - 1280px - 桌面 */
/* 大于 1280px - 大屏 */

@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
```

---

## HTML报告模板结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>报告标题</title>

  <!-- 样式表 -->
  <link rel="stylesheet" href="styles.css">

  <!-- 数据可视化库 -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/plotly.js-dist.min.js"></script>

  <!-- 字体 -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
  <!-- 导航栏 -->
  <nav class="report-nav">
    <div class="nav-container">
      <h1 class="nav-title">报告标题</h1>
      <div class="nav-actions">
        <button class="btn btn-outline" onclick="window.print()">打印</button>
        <button class="btn btn-primary" onclick="exportData()">导出数据</button>
      </div>
    </div>
  </nav>

  <!-- 主内容区 -->
  <main class="report-container">
    <!-- 执行摘要 -->
    <section class="report-section executive-summary">
      <div class="section-header">
        <h2>执行摘要</h2>
        <p class="section-meta">更新时间：2025年1月</p>
      </div>
      <div class="summary-grid">
        <!-- KPI卡片 -->
        <div class="kpi-card">
          <div class="kpi-value">¥1,234,567</div>
          <div class="kpi-label">总收入</div>
          <div class="kpi-change positive">+23.5%</div>
        </div>
        <!-- 更多KPI卡片... -->
      </div>
    </section>

    <!-- 数据可视化 -->
    <section class="report-section data-viz">
      <div class="section-header">
        <h2>数据分析</h2>
      </div>
      <div class="chart-grid">
        <div class="chart-card">
          <canvas id="lineChart"></canvas>
        </div>
        <!-- 更多图表... -->
      </div>
    </section>

    <!-- 详细内容 -->
    <section class="report-section content">
      <div class="section-header">
        <h2>详细分析</h2>
      </div>
      <div class="prose">
        <!-- 富文本内容 -->
      </div>
    </section>
  </main>

  <!-- 页脚 -->
  <footer class="report-footer">
    <p>&copy; 2025 报告生成器. 保留所有权利。</p>
  </footer>

  <!-- 脚本 -->
  <script src="scripts.js"></script>
</body>
</html>
```

---

## 核心组件样式

### KPI卡片（KPI Card）

```css
.kpi-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: var(--space-6);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.kpi-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.kpi-value {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  line-height: var(--leading-tight);
}

.kpi-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin-top: var(--space-2);
}

.kpi-change {
  display: inline-flex;
  align-items: center;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  margin-top: var(--space-3);
  padding: var(--space-1) var(--space-2);
  border-radius: 6px;
}

.kpi-change.positive {
  color: var(--color-success);
  background: rgba(16, 185, 129, 0.1);
}

.kpi-change.negative {
  color: var(--color-error);
  background: rgba(239, 68, 68, 0.1);
}
```

### 图表卡片（Chart Card）

```css
.chart-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: var(--space-6);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chart-card .chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.chart-card .chart-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.chart-card .chart-actions {
  display: flex;
  gap: var(--space-2);
}

.chart-card .chart-container {
  position: relative;
  height: 300px;
}
```

### 内容排版（Typography）

```css
.prose {
  max-width: 65ch;
  line-height: var(--leading-relaxed);
}

.prose h2 {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin-top: var(--space-8);
  margin-bottom: var(--space-4);
}

.prose h3 {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-top: var(--space-6);
  margin-bottom: var(--space-3);
}

.prose p {
  margin-bottom: var(--space-4);
  color: var(--text-secondary);
}

.prose ul, .prose ol {
  margin-bottom: var(--space-4);
  padding-left: var(--space-6);
}

.prose li {
  margin-bottom: var(--space-2);
  color: var(--text-secondary);
}

.prose strong {
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.prose code {
  font-family: var(--font-mono);
  font-size: 0.875em;
  background: var(--bg-tertiary);
  padding: 0.2em 0.4em;
  border-radius: 4px;
}

.prose blockquote {
  border-left: 4px solid var(--color-primary);
  padding-left: var(--space-4);
  color: var(--text-secondary);
  font-style: italic;
}
```

---

## 响应式布局

### 移动优先网格系统

```css
/* 默认：移动端 - 单列 */
.summary-grid {
  display: grid;
  gap: var(--space-4);
  grid-template-columns: 1fr;
}

/* 平板：2列 */
@media (min-width: 640px) {
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 桌面：4列 */
@media (min-width: 1024px) {
  .summary-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* 图表网格 */
.chart-grid {
  display: grid;
  gap: var(--space-6);
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .chart-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1280px) {
  .chart-grid-3 {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

---

## 交互功能

### 图表初始化（Chart.js）

```javascript
// 线图
function createLineChart(canvasId, data, options = {}) {
  const ctx = document.getElementById(canvasId).getContext('2d');

  const defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: {
          font: {
            family: "'Inter', sans-serif",
            size: 12
          },
          color: '#6b7280'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(17, 24, 39, 0.9)',
        titleFont: { family: "'Inter', sans-serif" },
        bodyFont: { family: "'Inter', sans-serif" },
        padding: 12,
        cornerRadius: 8
      }
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: {
          font: { family: "'Inter', sans-serif", size: 11 },
          color: '#9ca3af'
        }
      },
      y: {
        grid: { color: '#f3f4f6' },
        ticks: {
          font: { family: "'Inter', sans-serif", size: 11 },
          color: '#9ca3af'
        }
      }
    }
  };

  return new Chart(ctx, {
    type: 'line',
    data: data,
    options: { ...defaultOptions, ...options }
  });
}

// 使用示例
const revenueData = {
  labels: ['1月', '2月', '3月', '4月', '5月', '6月'],
  datasets: [{
    label: '收入',
    data: [65000, 72000, 81000, 89000, 95000, 108000],
    borderColor: '#2563eb',
    backgroundColor: 'rgba(37, 99, 235, 0.1)',
    borderWidth: 2,
    fill: true,
    tension: 0.4
  }]
};

createLineChart('lineChart', revenueData);
```

### 数据表格（带排序和搜索）

```javascript
function createDataTable(tableId, data, columns) {
  const table = document.getElementById(tableId);
  let currentData = [...data];
  let sortColumn = null;
  let sortDirection = 'asc';

  function renderTable() {
    const thead = table.querySelector('thead');
    const tbody = table.querySelector('tbody');

    // 渲染表头
    thead.innerHTML = `
      <tr>
        ${columns.map(col => `
          <th class="sortable" data-column="${col.key}">
            ${col.label}
            <span class="sort-indicator"></span>
          </th>
        `).join('')}
      </tr>
    `;

    // 渲染数据
    tbody.innerHTML = currentData.map(row => `
      <tr>
        ${columns.map(col => `
          <td>${row[col.key]}</td>
        `).join('')}
      </tr>
    `).join('');

    // 绑定排序事件
    thead.querySelectorAll('.sortable').forEach(th => {
      th.addEventListener('click', () => {
        const column = th.dataset.column;
        if (sortColumn === column) {
          sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
          sortColumn = column;
          sortDirection = 'asc';
        }
        sortData(column, sortDirection);
        renderTable();
      });
    });
  }

  function sortData(column, direction) {
    currentData.sort((a, b) => {
      if (a[column] < b[column]) return direction === 'asc' ? -1 : 1;
      if (a[column] > b[column]) return direction === 'asc' ? 1 : -1;
      return 0;
    });
  }

  renderTable();
  return { sortData, refresh: renderTable };
}
```

---

## 最佳实践清单

### ✅ 设计规范

- [ ] 最多使用2-3种字体
- [ ] 建立清晰的字号层级（6-7级）
- [ ] 使用一致的间距系统（8px基准）
- [ ] 限制颜色使用（主色+3-4种辅助色）
- [ ] 确保文字对比度≥4.5:1

### ✅ 响应式设计

- [ ] 移动优先设计
- [ ] 至少3个断点（640px, 768px, 1024px）
- [ ] 触摸目标最小44x44px
- [ ] 图片使用现代格式（WebP）
- [ ] 禁用双击缩放但保持滚动

### ✅ 性能优化

- [ ] 延迟加载非首屏内容
- [ ] 压缩CSS和JavaScript
- [ ] 使用CDN加载库文件
- [ ] 图片添加width/height属性
- [ ] 启用浏览器缓存

### ✅ 可访问性

- [ ] 所有图片添加alt属性
- [ ] 链接添加描述性文字
- [ ] 使用语义化HTML标签
- [ ] 键盘导航可用
- [ ] ARIA标签适当使用

### ✅ 数据可视化

- [ ] 图表添加标题和标签
- [ ] 使用一致的颜色方案
- [ ] 避免使用3D效果
- [ ] 数据点不超过7个
- [ ] 提供数据表格作为替代

---

## 快速开始命令

```bash
# 创建新报告项目
/html create my-report

# 添加KPI组件
/html add kpi --value "¥1,234,567" --label "收入" --change "+23.5%"

# 添加图表
/html add chart --type line --data revenue.json

# 生成报告
/html build

# 预览报告
/html preview

# 导出为PDF
/html export pdf
```

---

## 示例数据结构

```json
{
  "metadata": {
    "title": "Q4 2024 财务报告",
    "subtitle": "季度业绩分析",
    "author": "财务部",
    "date": "2024-12-31",
    "version": "1.0"
  },
  "kpi": [
    {
      "id": "revenue",
      "label": "总收入",
      "value": 1234567,
      "format": "currency",
      "change": 23.5,
      "period": "同比"
    },
    {
      "id": "users",
      "label": "活跃用户",
      "value": 45678,
      "format": "number",
      "change": 12.3,
      "period": "环比"
    }
  ],
  "charts": [
    {
      "id": "revenue-trend",
      "type": "line",
      "title": "收入趋势",
      "data": {
        "labels": ["1月", "2月", "3月", "4月", "5月", "6月"],
        "datasets": [{
          "label": "收入",
          "data": [65000, 72000, 81000, 89000, 95000, 108000]
        }]
      }
    }
  ]
}
```

---

## 技术栈建议

| 组件 | 推荐工具 | 说明 |
|------|----------|------|
| 核心框架 | 原生HTML/CSS/JS | 轻量、可控 |
| 图表库 | Chart.js / Plotly | 功能完整、文档完善 |
| 样式系统 | CSS Variables | 易于自定义 |
| 构建工具 | Vite / esbuild | 快速构建 |
| 打包工具 | 基于工具链 | 可选 |
| PDF导出 | html2pdf.js / Puppeteer | 服务端/客户端 |
| 数据处理 | 自定义 / D3.js | 按需选择 |

---

> **注意**：此技能专注于生成高质量的HTML报告。对于简单的静态文档，考虑使用Markdown；对于需要实时协作的场景，考虑使用Notion格式。
