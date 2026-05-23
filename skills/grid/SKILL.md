# Bento Grid Report Generator

> **生成Bento Grid卡片布局报告的技能包**
>
> 核心能力：模块化网格、信息密度优化、视觉层级、2025设计趋势

---

## 技能概述

生成基于Bento Grid（便当盒）布局的模块化卡片报告，将信息组织到清晰的独立区域中。

**适用场景**：
- 仪表盘和KPI报告
- 执行摘要
- 产品特性展示
- 数据概览
- 营销材料

**设计来源**：
- 日本便当盒（Bento）启发
- 2024-2025持续流行的UI趋势
- Apple、Linear等公司采用的设计语言

---

## 核心设计原则

### 1. 网格系统（Grid System）

```css
/* Bento Grid基础网格 */
.bento-grid {
  display: grid;
  gap: 1rem;
  padding: 1rem;

  /* 默认：移动端单列 */
  grid-template-columns: 1fr;
}

/* 平板：2列 */
@media (min-width: 640px) {
  .bento-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 桌面：4列 */
@media (min-width: 1024px) {
  .bento-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* 大屏：6列 */
@media (min-width: 1280px) {
  .bento-grid {
    grid-template-columns: repeat(6, 1fr);
    gap: 1.5rem;
    padding: 2rem;
  }
}
```

### 2. 卡片尺寸系统

```css
/* 卡片跨度类 */
.bento-card {
  /* 默认：1x1 */
  grid-column: span 1;
  grid-row: span 1;
}

/* 小卡片：1x1（默认） */
.card-sm {
  grid-column: span 1;
  grid-row: span 1;
}

/* 中等卡片：2x1（宽） */
.card-md {
  grid-column: span 2;
  grid-row: span 1;
}

/* 中等卡片：1x2（高） */
.card-md-tall {
  grid-column: span 1;
  grid-row: span 2;
}

/* 大卡片：2x2 */
.card-lg {
  grid-column: span 2;
  grid-row: span 2;
}

/* 超大卡片：3x2 */
.card-xl {
  grid-column: span 3;
  grid-row: span 2;
}

/* 全宽卡片 */
.card-full {
  grid-column: 1 / -1;
  grid-row: span 1;
}

/* 响应式调整 */
@media (max-width: 640px) {
  .card-md,
  .card-md-tall,
  .card-lg,
  .card-xl,
  .card-full {
    grid-column: span 1;
    grid-row: span auto;
  }
}
```

### 3. 内容分区原则

```yaml
# Bento Grid内容分区
content_zones:
  # 主隔间（Primary Compartment）
  primary:
    size: "2x2 或 3x2"
    content_types:
      - 核心KPI
      - 主要图表
      - 关键洞察
    visual_weight: "最高"
    priority: "最先关注"

  # 次隔间（Secondary Compartment）
  secondary:
    size: "2x1 或 1x2"
    content_types:
      - 次要指标
      - 趋势图表
      - 进度状态
    visual_weight: "中等"
    priority: "次要关注"

  # 三级空间（Tertiary Space）
  tertiary:
    size: "1x1"
    content_types:
      - 小指标
      - 状态标签
      - 趋势指示器
      - 注释说明
    visual_weight: "低"
    priority: "参考信息"
```

---

## HTML模板结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bento Grid Report</title>
  <link rel="stylesheet" href="bento-grid.css">
</head>
<body>
  <div class="report-container">
    <!-- 报告头部 -->
    <header class="report-header">
      <h1>Q4 财务报告</h1>
      <p class="report-meta">2024年第四季度 | 更新于 2025-01-10</p>
    </header>

    <!-- Bento Grid 主容器 -->
    <main class="bento-grid">
      <!-- 主KPI卡片（2x2） -->
      <div class="bento-card card-lg card-primary">
        <div class="card-header">
          <span class="card-icon">💰</span>
          <h3 class="card-title">总收入</h3>
        </div>
        <div class="card-content">
          <div class="big-number">¥12,345,678</div>
          <div class="trend-indicator positive">
            <svg width="16" height="16" viewBox="0 0 16 16">
              <path d="M8 4v8M4 8l4-4 4 4" stroke="currentColor" fill="none"/>
            </svg>
            +23.5%
          </div>
          <p class="card-caption">较上季度增长</p>
        </div>
        <div class="card-chart">
          <canvas id="revenueChart"></canvas>
        </div>
      </div>

      <!-- 用户增长卡片（1x2） -->
      <div class="bento-card card-md-tall card-secondary">
        <div class="card-header">
          <span class="card-icon">👥</span>
          <h3 class="card-title">用户增长</h3>
        </div>
        <div class="card-content">
          <div class="big-number">45,678</div>
          <div class="trend-indicator positive">+12.3%</div>
          <div class="stat-list">
            <div class="stat-item">
              <span class="stat-label">新用户</span>
              <span class="stat-value">5,234</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">活跃用户</span>
              <span class="stat-value">38,456</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">流失率</span>
              <span class="stat-value negative">-2.1%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 转化率卡片（1x1） -->
      <div class="bento-card card-sm">
        <div class="card-header">
          <span class="card-icon">📊</span>
          <h3 class="card-title">转化率</h3>
        </div>
        <div class="card-content">
          <div class="big-number">3.2%</div>
          <div class="trend-indicator positive">+0.5pp</div>
        </div>
      </div>

      <!-- 客单价卡片（1x1） -->
      <div class="bento-card card-sm">
        <div class="card-header">
          <span class="card-icon">💳</span>
          <h3 class="card-title">客单价</h3>
        </div>
        <div class="card-content">
          <div class="big-number">¥268</div>
          <div class="trend-indicator negative">-5.2%</div>
        </div>
      </div>

      <!-- 进度卡片（2x1） -->
      <div class="bento-card card-md">
        <div class="card-header">
          <span class="card-icon">🎯</span>
          <h3 class="card-title">年度目标进度</h3>
        </div>
        <div class="card-content">
          <div class="progress-list">
            <div class="progress-item">
              <span class="progress-label">收入目标</span>
              <div class="progress-bar">
                <div class="progress-fill" style="width: 85%">
                  <span class="progress-value">85%</span>
                </div>
              </div>
            </div>
            <div class="progress-item">
              <span class="progress-label">用户增长</span>
              <div class="progress-bar">
                <div class="progress-fill" style="width: 92%">
                  <span class="progress-value">92%</span>
                </div>
              </div>
            </div>
            <div class="progress-item">
              <span class="progress-label">市场份额</span>
              <div class="progress-bar">
                <div class="progress-fill" style="width: 67%">
                  <span class="progress-value">67%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 趋势卡片（2x1） -->
      <div class="bento-card card-md">
        <div class="card-header">
          <span class="card-icon">📈</span>
          <h3 class="card-title">月度趋势</h3>
        </div>
        <div class="card-content">
          <canvas id="trendChart"></canvas>
        </div>
      </div>

      <!-- 状态列表卡片（1x2） -->
      <div class="bento-card card-md-tall">
        <div class="card-header">
          <span class="card-icon">📋</span>
          <h3 class="card-title">项目状态</h3>
        </div>
        <div class="card-content">
          <div class="status-list">
            <div class="status-item">
              <div class="status-icon completed">✓</div>
              <div class="status-info">
                <span class="status-title">网站改版</span>
                <span class="status-desc">已完成</span>
              </div>
            </div>
            <div class="status-item">
              <div class="status-icon in-progress">⟳</div>
              <div class="status-info">
                <span class="status-title">移动端优化</span>
                <span class="status-desc">进行中 75%</span>
              </div>
            </div>
            <div class="status-item">
              <div class="status-icon pending">○</div>
              <div class="status-info">
                <span class="status-title">数据迁移</span>
                <span class="status-desc">计划中</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 洞察卡片（2x1） -->
      <div class="bento-card card-md card-insight">
        <div class="card-header">
          <span class="card-icon">💡</span>
          <h3 class="card-title">关键洞察</h3>
        </div>
        <div class="card-content">
          <p class="insight-text">移动端用户占比首次超过60%，建议加大移动端投入。</p>
          <button class="btn-link">查看详情 →</button>
        </div>
      </div>

      <!-- 快速操作卡片（1x1） -->
      <div class="bento-card card-sm card-action">
        <div class="card-content">
          <button class="btn-primary">导出报告</button>
        </div>
      </div>

    </main>
  </div>

  <script src="bento-grid.js"></script>
</body>
</html>
```

---

## 核心样式

### 卡片基础样式

```css
/* 卡片基础 */
.bento-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  border: 1px solid #f3f4f6;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  min-height: 140px;
}

.bento-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.card-icon {
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  background: #f9fafb;
  border-radius: 12px;
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

/* 卡片内容 */
.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* 大数字 */
.big-number {
  font-size: clamp(1.5rem, 4vw, 2.5rem);
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1;
  margin-bottom: 0.5rem;
}

/* 趋势指示器 */
.trend-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 50px;
  margin-bottom: 0.5rem;
  width: fit-content;
}

.trend-indicator.positive {
  color: #059669;
  background: #ecfdf5;
}

.trend-indicator.negative {
  color: #dc2626;
  background: #fef2f2;
}

/* 卡片说明 */
.card-caption {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

/* 特殊卡片类型 */
.card-primary {
  border-left: 4px solid #2563eb;
}

.card-insight {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  color: white;
}

.card-insight .card-title,
.card-insight .insight-text {
  color: white;
}

.card-action {
  background: transparent;
  border: 2px dashed #e5e7eb;
  box-shadow: none;
}

.card-action:hover {
  border-color: #2563eb;
  box-shadow: none;
}
```

### 统计列表

```css
/* 统计列表 */
.stat-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 8px;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.stat-value {
  font-size: 1rem;
  font-weight: 600;
  color: #1a1a1a;
}

.stat-value.negative {
  color: #dc2626;
}
```

### 进度条

```css
/* 进度列表 */
.progress-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.progress-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.progress-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #4a4a4a;
  display: flex;
  justify-content: space-between;
}

.progress-bar {
  height: 8px;
  background: #f3f4f6;
  border-radius: 50px;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%);
  border-radius: 50px;
  transition: width 0.5s ease;
  position: relative;
}

.progress-value {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.625rem;
  font-weight: 600;
  color: white;
}
```

### 状态列表

```css
/* 状态列表 */
.status-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 10px;
}

.status-icon {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
}

.status-icon.completed {
  background: #ecfdf5;
  color: #059669;
}

.status-icon.in-progress {
  background: #dbeafe;
  color: #2563eb;
}

.status-icon.pending {
  background: #f3f4f6;
  color: #6b7280;
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.status-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1a1a1a;
}

.status-desc {
  font-size: 0.75rem;
  color: #6b7280;
}
```

### 按钮样式

```css
/* 按钮 */
.btn-primary {
  width: 100%;
  padding: 0.75rem 1rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-link {
  background: none;
  border: none;
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  text-decoration: underline;
  padding: 0;
}
```

---

## 图表配置

```javascript
// 图表配置（紧凑型）
const compactChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: 'rgba(17, 24, 39, 0.9)',
      titleFont: { size: 12 },
      bodyFont: { size: 11 },
      padding: 8,
      cornerRadius: 6
    }
  },
  scales: {
    x: {
      display: false,
      grid: { display: false }
    },
    y: {
      display: false,
      grid: { display: false }
    }
  },
  elements: {
    point: {
      radius: 0,
      hitRadius: 10
    },
    line: {
      tension: 0.4,
      borderWidth: 2
    }
  }
};

// 迷你图表（Sparkline）
function createSparkline(canvasId, data, color) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.map((_, i) => i),
      datasets: [{
        data: data,
        borderColor: color,
        backgroundColor: `${color}10`,
        fill: true
      }]
    },
    options: compactChartOptions
  });
}
```

---

## 响应式布局

```css
/* 移动端优化 */
@media (max-width: 640px) {
  .bento-grid {
    gap: 0.75rem;
    padding: 0.75rem;
  }

  .bento-card {
    padding: 1rem;
    min-height: auto;
  }

  .big-number {
    font-size: 1.75rem;
  }

  .card-icon {
    width: 2rem;
    height: 2rem;
    font-size: 1.25rem;
  }
}

/* 平板优化 */
@media (min-width: 640px) and (max-width: 1024px) {
  .bento-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .card-lg {
    grid-column: span 2;
    grid-row: span 2;
  }

  .card-xl {
    grid-column: span 2;
    grid-row: span 2;
  }
}

/* 大屏优化 */
@media (min-width: 1280px) {
  .bento-grid {
    max-width: 1400px;
    margin: 0 auto;
  }
}
```

---

## 快速开始命令

```bash
# 创建Bento Grid报告
/grid create dashboard

# 添加主KPI卡片
/grid add card --type primary --size "2x2" --title "收入" --value "¥1,234,567"

# 添加次要卡片
/grid add card --type secondary --size "1x1" --title "转化率" --value "3.2%"

# 生成布局
/grid build

# 预览
/grid preview
```

---

## 数据结构模板

```json
{
  "layout": "bento-grid",
  "columns": 4,
  "gap": "1rem",
  "cards": [
    {
      "id": "revenue",
      "type": "primary",
      "size": {
        "width": 2,
        "height": 2
      },
      "content": {
        "icon": "💰",
        "title": "总收入",
        "value": 12345678,
        "format": "currency",
        "trend": {
          "value": 23.5,
          "direction": "up"
        },
        "chart": {
          "type": "line",
          "data": [100, 120, 115, 140, 135, 160]
        }
      }
    },
    {
      "id": "users",
      "type": "secondary",
      "size": {
        "width": 1,
        "height": 2
      },
      "content": {
        "icon": "👥",
        "title": "用户增长",
        "value": 45678,
        "stats": [
          {"label": "新用户", "value": 5234},
          {"label": "活跃用户", "value": 38456},
          {"label": "流失率", "value": -2.1}
        ]
      }
    }
  ]
}
```

---

## 最佳实践清单

### ✅ 内容组织

- [ ] 主KPI占据最大空间（2x2或3x2）
- [ ] 相关内容逻辑分组
- [ ] 重要信息左上角优先
- [ ] 保持视觉平衡
- [ ] 限制卡片数量（8-12个）

### ✅ 卡片设计

- [ ] 圆角统一（12-16px）
- [ ] 间距一致（8px倍数）
- [ ] 阴影微妙（0-4px）
- [ ] 悬停效果微妙
- [ ] 图标大小统一

### ✅ 数据展示

- [ ] 大数字清晰易读
- [ ] 趋势颜色一致（绿涨红跌）
- [ ] 进度条有百分比
- [ ] 图表简洁无干扰
- [ ] 数据标签清晰

### ✅ 响应式设计

- [ ] 移动端单列
- [ ] 平板2列
- [ ] 桌面4-6列
- [ ] 卡片自动堆叠
- [ ] 触摸目标足够大

---

## 技术栈建议

| 组件 | 推荐工具 | 说明 |
|------|----------|------|
| 布局 | CSS Grid | 原生网格 |
| 图表 | Chart.js | 轻量图表库 |
| 图标 | Emoji / Lucide | 一致性 |
| 构建 | Vite | 快速开发 |
| 部署 | 静态托管 | 任何平台 |

---

> **注意**：Bento Grid适合KPI展示和仪表盘场景。对于大量文本内容，考虑使用其他格式。
