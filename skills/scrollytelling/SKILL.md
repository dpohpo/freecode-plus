# Scrollytelling Report Generator

> **生成滚动叙事数据报告的技能包**
>
> 核心能力：滚动触发动画、渐进式叙事、数据可视化、沉浸式体验

---

## 技能概述

生成基于滚动触发的交互式数据叙事报告，将复杂数据转化为引人入胜的故事体验。

**适用场景**：
- 年度报告
- 数据新闻
- 公共政策传播
- 品牌故事
- 调查报告

**灵感来源**：
- Gapminder (Hans Rosling)
- NY Times COVID Dashboard
- Spotify Wrapped
- FiveThirtyEight

---

## 核心设计原则

### 1. 叙事结构（Story Arc）

```javascript
// 故事结构模板
const storyStructure = {
  hook: {
    title: "引人入胜的开头",
    content: "用令人震惊的数据或问题抓住读者注意力",
    trigger: "screenPosition > 0.1"
  },
  context: {
    title: "背景介绍",
    content: "提供必要的上下文信息",
    trigger: "screenPosition > 0.2"
  },
  conflict: {
    title: "问题揭示",
    content: "展示核心问题或挑战",
    trigger: "screenPosition > 0.4"
  },
  journey: {
    title: "探索过程",
    content: "逐步展开数据和分析",
    trigger: "screenPosition > 0.5"
  },
  revelation: {
    title: "关键发现",
    content: "最重要的洞察",
    trigger: "screenPosition > 0.7"
  },
  resolution: {
    title: "结论与行动",
    content: "总结和可操作的建议",
    trigger: "screenPosition > 0.9"
  }
};
```

### 2. 滚动触发机制

```javascript
// Intersection Observer API
class ScrollytellingEngine {
  constructor(options = {}) {
    this.thresholds = options.thresholds || [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1];
    this.rootMargin = options.rootMargin || '-100px 0px -100px 0px';
    this.callbacks = new Map();

    this.observer = new IntersectionObserver(
      this.handleIntersect.bind(this),
      { threshold: this.thresholds, rootMargin: this.rootMargin }
    );
  }

  observe(element, callback) {
    this.callbacks.set(element, callback);
    this.observer.observe(element);
  }

  handleIntersect(entries) {
    entries.forEach(entry => {
      const callback = this.callbacks.get(entry.target);
      if (callback) {
        callback({
          element: entry.target,
          isVisible: entry.isIntersecting,
          intersectionRatio: entry.intersectionRatio,
          boundingClientRect: entry.boundingClientRect
        });
      }
    });
  }

  disconnect() {
    this.observer.disconnect();
    this.callbacks.clear();
  }
}

// 使用示例
const engine = new ScrollytellingEngine();

document.querySelectorAll('.story-section').forEach(section => {
  engine.observe(section, (data) => {
    if (data.isVisible) {
      section.classList.add('active');
      updateVisualization(section.dataset.step, data.intersectionRatio);
    }
  });
});
```

### 3. 渐进式信息揭示

```css
/* 渐进式显示动画 */
.story-section {
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.story-section.active {
  opacity: 1;
  transform: translateY(0);
}

/* 子元素依次显示 */
.story-section.active > * {
  opacity: 0;
  animation: fadeSlideIn 0.6s ease-out forwards;
}

.story-section.active > *:nth-child(1) { animation-delay: 0s; }
.story-section.active > *:nth-child(2) { animation-delay: 0.1s; }
.story-section.active > *:nth-child(3) { animation-delay: 0.2s; }
.story-section.active > *:nth-child(4) { animation-delay: 0.3s; }
.story-section.active > *:nth-child(5) { animation-delay: 0.4s; }

@keyframes fadeSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

---

## HTML模板结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>数据叙事报告</title>
  <link rel="stylesheet" href="scrollytelling.css">
</head>
<body>
  <!-- 固定导航 -->
  <nav class="story-nav">
    <div class="nav-progress">
      <div class="progress-bar"></div>
    </div>
    <div class="nav-chapters">
      <a href="#chapter-1" class="chapter-link active">第一章</a>
      <a href="#chapter-2" class="chapter-link">第二章</a>
      <a href="#chapter-3" class="chapter-link">第三章</a>
    </div>
  </nav>

  <!-- 视觉锚点（固定背景图表） -->
  <div class="viz-container">
    <canvas id="mainChart"></canvas>
    <div class="viz-caption">
      <span class="viz-title">数据可视化</span>
      <span class="viz-description">滚动探索数据变化</span>
    </div>
  </div>

  <!-- 故事内容层（滚动触发） -->
  <main class="story-content">
    <!-- 第一章 -->
    <section id="chapter-1" class="story-section" data-step="1">
      <div class="section-background"></div>
      <div class="section-content">
        <div class="chapter-label">第一章</div>
        <h1>引人入胜的开头</h1>
        <p class="lead">用一个令人震惊的数据或问题开始你的故事...</p>
        <div class="data-highlight">
          <span class="big-number">1,234,567</span>
          <span class="number-label">这个数字改变了 everything</span>
        </div>
      </div>
    </section>

    <!-- 第二章 -->
    <section id="chapter-2" class="story-section" data-step="2">
      <div class="section-background"></div>
      <div class="section-content">
        <div class="chapter-label">第二章</div>
        <h2>背景与上下文</h2>
        <p>了解问题的来龙去脉...</p>
        <div class="timeline">
          <div class="timeline-item">
            <span class="year">2020</span>
            <span class="event">起始点</span>
          </div>
          <div class="timeline-item">
            <span class="year">2023</span>
            <span class="event">转折点</span>
          </div>
          <div class="timeline-item">
            <span class="year">2025</span>
            <span class="event">现在</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 第三章 -->
    <section id="chapter-3" class="story-section" data-step="3">
      <div class="section-content">
        <div class="chapter-label">第三章</div>
        <h2>关键发现</h2>
        <p>最重要的洞察...</p>
        <div class="insight-card">
          <div class="insight-icon">💡</div>
          <h3>核心洞察</h3>
          <p>用一句话总结最重要的发现</p>
          <ul class="insight-points">
            <li>洞察点一</li>
            <li>洞察点二</li>
            <li>洞察点三</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- 结论 -->
    <section id="conclusion" class="story-section conclusion" data-step="4">
      <div class="section-content">
        <h2>结论与行动</h2>
        <p>基于以上分析，我们建议...</p>
        <div class="action-cards">
          <div class="action-card">
            <h3>行动一</h3>
            <p>具体行动描述</p>
          </div>
          <div class="action-card">
            <h3>行动二</h3>
            <p>具体行动描述</p>
          </div>
          <div class="action-card">
            <h3>行动三</h3>
            <p>具体行动描述</p>
          </div>
        </div>
      </div>
    </section>
  </main>

  <script src="scrollytelling.js"></script>
</body>
</html>
```

---

## 核心样式

### 故事章节

```css
/* 故事章节基础样式 */
.story-section {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  position: relative;
}

.story-section .section-content {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}

/* 章节标签 */
.chapter-label {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: rgba(37, 99, 235, 0.1);
  color: #2563eb;
  border-radius: 50px;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
}

/* 标题 */
.story-section h1 {
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 1.5rem;
  color: #1a1a1a;
}

.story-section h2 {
  font-size: clamp(1.5rem, 4vw, 2.5rem);
  font-weight: 600;
  line-height: 1.3;
  margin-bottom: 1.5rem;
  color: #1a1a1a;
}

/* 正文 */
.story-section p {
  font-size: 1.125rem;
  line-height: 1.75;
  color: #4a4a4a;
  margin-bottom: 1.5rem;
}

.story-section .lead {
  font-size: 1.5rem;
  color: #6b7280;
}
```

### 数据高亮

```css
/* 大数字展示 */
.data-highlight {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  margin: 2rem 0;
}

.big-number {
  font-size: clamp(3rem, 10vw, 6rem);
  font-weight: 700;
  color: #2563eb;
  line-height: 1;
  animation: countUp 2s ease-out forwards;
}

.number-label {
  font-size: 1rem;
  color: #6b7280;
}

@keyframes countUp {
  from {
    opacity: 0;
    transform: scale(0.5);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
```

### 洞察卡片

```css
/* 洞察卡片 */
.insight-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin: 2rem 0;
  text-align: left;
}

.insight-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.insight-card h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #1a1a1a;
}

.insight-points {
  list-style: none;
  padding: 0;
}

.insight-points li {
  padding: 0.75rem 0;
  padding-left: 2rem;
  position: relative;
  color: #4a4a4a;
}

.insight-points li::before {
  content: "✓";
  position: absolute;
  left: 0;
  color: #2563eb;
  font-weight: bold;
}
```

### 行动卡片

```css
/* 行动卡片网格 */
.action-cards {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  margin: 2rem 0;
}

.action-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.action-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: #1a1a1a;
}

.action-card p {
  font-size: 1rem;
  color: #6b7280;
  margin: 0;
}
```

---

## 视觉化组件

### 时间线

```css
/* 时间线 */
.timeline {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin: 3rem 0;
  flex-wrap: wrap;
}

.timeline-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  position: relative;
}

.timeline-item .year {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2563eb;
}

.timeline-item .event {
  font-size: 0.875rem;
  color: #6b7280;
  text-align: center;
}

.timeline-item:not(:last-child)::after {
  content: "";
  position: absolute;
  top: 1rem;
  left: calc(100% + 1rem);
  width: 2rem;
  height: 2px;
  background: #e5e7eb;
}
```

### 进度指示器

```css
/* 导航进度 */
.story-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #e5e7eb;
}

.nav-progress {
  height: 3px;
  background: #f3f4f6;
}

.progress-bar {
  height: 100%;
  background: #2563eb;
  width: 0%;
  transition: width 0.1s ease-out;
}

.nav-chapters {
  display: flex;
  justify-content: center;
  gap: 2rem;
  padding: 1rem;
}

.chapter-link {
  color: #6b7280;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: color 0.2s;
}

.chapter-link:hover,
.chapter-link.active {
  color: #2563eb;
}
```

---

## JavaScript功能

### 滚动进度跟踪

```javascript
// 滚动进度
function updateScrollProgress() {
  const scrollTop = window.scrollY;
  const docHeight = document.documentElement.scrollHeight - window.innerHeight;
  const progress = (scrollTop / docHeight) * 100;

  document.querySelector('.progress-bar').style.width = `${progress}%`;

  // 更新活跃章节
  document.querySelectorAll('.story-section').forEach(section => {
    const rect = section.getBoundingClientRect();
    if (rect.top <= window.innerHeight / 2 && rect.bottom >= window.innerHeight / 2) {
      const chapterId = section.id;
      document.querySelectorAll('.chapter-link').forEach(link => {
        link.classList.toggle('active', link.getAttribute('href') === `#${chapterId}`);
      });
    }
  });
}

window.addEventListener('scroll', updateScrollProgress);
```

### 数字计数动画

```javascript
// 数字计数动画
function animateNumber(element, target, duration = 2000) {
  const start = 0;
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);

    // 缓动函数
    const easeOut = 1 - Math.pow(1 - progress, 3);
    const current = Math.floor(start + (target - start) * easeOut);

    element.textContent = current.toLocaleString();

    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }

  requestAnimationFrame(update);
}

// 使用
document.querySelectorAll('.big-number').forEach(el => {
  const target = parseInt(el.textContent.replace(/,/g, ''));
  animateNumber(el, target);
});
```

### 图表同步更新

```javascript
// 根据滚动位置更新图表
function updateVisualization(step, ratio) {
  const chart = Chart.getChart('mainChart');

  if (!chart) return;

  const configs = {
    1: {
      data: [65, 72, 81, 89, 95, 108],
      label: '收入趋势'
    },
    2: {
      data: [1000, 1500, 2000, 2800, 3500, 4200],
      label: '用户增长'
    },
    3: {
      data: [23, 25, 21, 28, 26, 30],
      label: '市场份额'
    },
    4: {
      data: [45, 52, 58, 62, 68, 72],
      label: '客户满意度'
    }
  };

  const config = configs[step];
  if (config) {
    chart.data.datasets[0].data = config.data;
    chart.data.datasets[0].label = config.label;
    chart.update('none'); // 无动画更新
  }
}
```

---

## 最佳实践清单

### ✅ 叙事设计

- [ ] 建立清晰的故事弧（开头-发展-高潮-结尾）
- [ ] 每个章节有明确的主题
- [ ] 用问题或数据作为钩子
- [ ] 渐进式揭示信息
- [ ] 在关键时刻给予情感冲击

### ✅ 交互设计

- [ ] 滚动触发动画流畅
- [ ] 视觉反馈及时
- [ ] 加载状态友好
- [ ] 移动端体验良好
- [ ] 提供跳转导航

### ✅ 数据可视化

- [ ] 图表与内容同步
- [ ] 动画不过度
- [ ] 颜色一致
- [ ] 图表添加说明
- [ ] 提供数据来源

### ✅ 性能优化

- [ ] 图片懒加载
- [ ] 使用Intersection Observer
- [ ] 防抖滚动事件
- [ ] 压缩资源文件
- [ ] CDN加载库文件

---

## 快速开始命令

```bash
# 创建新的滚动叙事报告
/scrollytelling create my-story

# 添加故事章节
/scrollytelling add chapter --title "第一章" --content "内容..."

# 添加数据可视化
/scrollytelling add viz --type chart --data data.json

# 预览
/scrollytelling preview

# 构建
/scrollytelling build
```

---

## 故事模板

```json
{
  "title": "数据叙事报告",
  "subtitle": "用数据讲述引人入胜的故事",
  "author": "作者",
  "date": "2025-01-10",

  "structure": {
    "hook": {
      "title": "令人震惊的数据",
      "content": "用一个数字抓住注意力",
      "vizType": "bigNumber"
    },
    "context": {
      "title": "背景介绍",
      "content": "提供上下文",
      "vizType": "timeline"
    },
    "conflict": {
      "title": "问题揭示",
      "content": "展示核心问题",
      "vizType": "comparison"
    },
    "journey": {
      "title": "探索过程",
      "content": "逐步展开分析",
      "vizType": "multiChart"
    },
    "revelation": {
      "title": "关键发现",
      "content": "最重要的洞察",
      "vizType": "insight"
    },
    "resolution": {
      "title": "结论与行动",
      "content": "可操作的建议",
      "vizType": "actionCards"
    }
  }
}
```

---

## 技术栈建议

| 组件 | 推荐工具 | 说明 |
|------|----------|------|
| 核心框架 | 原生HTML/CSS/JS | 轻量可控 |
| 滚动检测 | Intersection Observer | 现代API |
| 图表库 | D3.js / Chart.js | 数据可视化 |
| 动画库 | GSAP | 专业动画 |
| 构建工具 | Vite | 快速开发 |
| 部署 | 静态托管 | Netlify/Vercel |

---

## 示例案例结构

```
scrollytelling-report/
├── index.html           # 主页面
├── css/
│   ├── base.css        # 基础样式
│   ├── story.css       # 故事样式
│   └── viz.css         # 可视化样式
├── js/
│   ├── engine.js       # 滚动引擎
│   ├── viz.js          # 图表配置
│   └── animations.js   # 动画效果
└── data/
    ├── story.json      # 故事内容
    └── charts.json     # 图表数据
```

---

> **注意**：Scrollytelling适合需要讲述数据故事的场景。制作成本较高，但参与度和传播潜力大。对于简单的数据展示，考虑使用标准HTML报告。
