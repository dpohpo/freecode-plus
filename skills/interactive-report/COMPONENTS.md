# Component Library

Complete implementation patterns for all report components. Each component
includes HTML structure and required CSS/JS. Combine with DESIGN-SYSTEM.md
for colors and animations.

---

## 1. Hero Section

Full viewport height. Animated gradient background, title, subtitle, pill
badges, and bounce-animated scroll arrow.

```html
<section id="hero" class="hero">
  <div class="hero-content">
    <h1 class="hero-title">REPORT TITLE</h1>
    <p class="hero-subtitle">Subtitle here</p>
    <p class="hero-description">Description text</p>
    <div class="hero-badges">
      <span class="badge">Badge 1</span>
      <span class="badge">Badge 2</span>
    </div>
  </div>
  <div class="scroll-arrow">
    <span>开始阅读</span>
    <svg><!-- down arrow --></svg>
  </div>
</section>
```

Key CSS: `min-height: 100vh; display: flex; align-items: center; justify-content: center;`
Background: Use `gradientShift` keyframes from DESIGN-SYSTEM.md.
Badges: `background: rgba(59,130,246,0.15); color: var(--accent-blue); border-radius: 20px; padding: 6px 16px; font-size: 0.85rem;`

---

## 2. Stat Cards

Row of 3-4 cards showing key metrics with countUp animation.

```html
<div class="grid-4 stagger-children">
  <div class="card stat-card fade-in-up">
    <div class="stat-icon">📊</div>
    <div class="stat-number" data-count-target="970" data-count-suffix="万+">0</div>
    <div class="stat-label">描述文字</div>
  </div>
  <!-- repeat -->
</div>
```

The `data-count-target` holds the numeric value. `data-count-suffix` and
`data-count-prefix` are appended/prepended after animation.

For percentages: `data-count-target="95" data-count-suffix="%"`
For currency: `data-count-target="4617" data-count-suffix="亿美元"`

---

## 3. Feature Cards

Icon + title + description. Hover glow effect.

```html
<div class="grid-2 stagger-children">
  <div class="card feature-card fade-in-up">
    <div class="feature-icon">🔗</div>
    <h3 class="feature-title">Feature Name</h3>
    <p class="feature-desc">Description...</p>
  </div>
</div>
```

Hover CSS: Add colored top-border or left-border glow. Icon background uses
matching accent color at 10% opacity.

---

## 4. SWOT Grid

2×2 grid. Each quadrant has its own accent color.

```html
<div class="swot-grid">
  <div class="swot-card swot-s fade-in-up">
    <h3>S 优势</h3>
    <ul><li>Point 1</li><li>Point 2</li></ul>
  </div>
  <div class="swot-card swot-w fade-in-up">...</div>
  <div class="swot-card swot-o fade-in-up">...</div>
  <div class="swot-card swot-t fade-in-up">...</div>
</div>
```

```css
.swot-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}
.swot-card {
  padding: 2rem;
  border-radius: 12px;
  transition: transform 0.3s, box-shadow 0.3s;
}
.swot-s { background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.2); }
.swot-w { background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2); }
.swot-o { background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.2); }
.swot-t { background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.2); }
.swot-card:hover {
  transform: scale(1.02);
  box-shadow: 0 0 30px currentColor; /* uses the card's text color for glow */
}
```

Mobile: `grid-template-columns: 1fr;`

---

## 5. Comparison Table

Scrollable table with one highlighted column.

```html
<div class="table-wrapper">
  <table class="comparison-table">
    <thead>
      <tr>
        <th>对比维度</th>
        <th>竞品 A</th>
        <th class="highlight-col">本项目</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>维度 1</td>
        <td>值</td>
        <td class="highlight-col">✅ 我们的值</td>
      </tr>
    </tbody>
  </table>
</div>
```

```css
.highlight-col {
  background: rgba(59,130,246,0.08);
  border-left: 2px solid var(--accent-blue);
  border-right: 2px solid var(--accent-blue);
}
thead .highlight-col {
  background: rgba(59,130,246,0.15);
  border-top: 2px solid var(--accent-blue);
}
/* Mobile horizontal scroll */
.table-wrapper { overflow-x: auto; }
```

---

## 6. Tab Component

For multi-view content (architecture, features, etc.).

```html
<div class="tabs">
  <div class="tab-nav">
    <button class="tab-btn active" data-tab="tab1">Tab 1</button>
    <button class="tab-btn" data-tab="tab2">Tab 2</button>
  </div>
  <div class="tab-content active" id="tab1">Content 1</div>
  <div class="tab-content" id="tab2">Content 2</div>
</div>
```

```javascript
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const tabGroup = btn.closest('.tabs');
    tabGroup.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    tabGroup.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    tabGroup.querySelector(`#${btn.dataset.tab}`).classList.add('active');
  });
});
```

Tab content switches with opacity fade: `.tab-content { display: none; opacity: 0; } .tab-content.active { display: block; opacity: 1; transition: opacity 0.3s; }`

---

## 7. Vertical Timeline

Left-aligned nodes with content cards on the right.

```html
<div class="timeline">
  <div class="timeline-item fade-in-up">
    <div class="timeline-node" data-phase="1"></div>
    <div class="timeline-connector"></div>
    <div class="timeline-content card">
      <div class="timeline-badge">阶段 1</div>
      <h4>Title</h4>
      <p>Description</p>
      <div class="timeline-meta">时间：第1-2周 | 成本：$0</div>
    </div>
  </div>
  <!-- repeat for each phase -->
</div>
```

```css
.timeline {
  position: relative;
  padding-left: 40px;
}
.timeline::before { /* vertical line */
  content: '';
  position: absolute;
  left: 7px;
  top: 0; bottom: 0;
  width: 2px;
  background: var(--bg-tertiary);
}
.timeline-item { position: relative; margin-bottom: 2rem; }
.timeline-node {
  position: absolute;
  left: -40px;
  /* centered on the line */
}
```

Scroll activation: Observer adds `.active` to `.timeline-node` when item enters
viewport. Connector line behind active nodes gets gradient fill.

---

## 8. Accordion

Collapsible sections for glossary or dense content.

```html
<div class="accordion">
  <div class="accordion-item">
    <button class="accordion-header">
      <span>Term</span>
      <span class="accordion-icon">+</span>
    </button>
    <div class="accordion-body">
      <p>Definition...</p>
    </div>
  </div>
</div>
```

```javascript
document.querySelectorAll('.accordion-header').forEach(header => {
  header.addEventListener('click', () => {
    const item = header.parentElement;
    const isOpen = item.classList.contains('open');
    // Optional: close others
    // item.parentElement.querySelectorAll('.accordion-item').forEach(i => i.classList.remove('open'));
    item.classList.toggle('open', !isOpen);
  });
});
```

```css
.accordion-body {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
}
.accordion-item.open .accordion-body {
  max-height: 500px; /* generous max */
}
.accordion-item.open .accordion-icon {
  transform: rotate(45deg);
}
```

---

## 9. Glossary Drawer (Side Panel)

Slides in from the right. Triggered by nav button.

```html
<div class="drawer-overlay" id="glossaryOverlay"></div>
<aside class="drawer" id="glossaryDrawer">
  <div class="drawer-header">
    <h3>术语表</h3>
    <button class="drawer-close">&times;</button>
  </div>
  <div class="drawer-body">
    <!-- accordion items here -->
  </div>
</aside>
```

```css
.drawer {
  position: fixed; top: 0; right: 0;
  width: 400px; max-width: 90vw; height: 100vh;
  background: var(--bg-secondary);
  transform: translateX(100%);
  transition: transform 0.3s ease;
  z-index: 1001;
  overflow-y: auto;
}
.drawer.open { transform: translateX(0); }
.drawer-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.5);
  opacity: 0; pointer-events: none;
  transition: opacity 0.3s;
  z-index: 1000;
}
.drawer-overlay.open { opacity: 1; pointer-events: auto; }
```

---

## 10. Progress Bars

Horizontal bars for cost comparison, market share, etc.

```html
<div class="progress-group fade-in-up">
  <div class="progress-item">
    <div class="progress-label">
      <span>阶段 1-2</span>
      <span>$185/月</span>
    </div>
    <div class="progress-track">
      <div class="progress-fill" style="--target-width: 15%"></div>
    </div>
  </div>
</div>
```

Fill animates from 0 to `--target-width` when `.visible` is added.

---

## 11. Risk Cards

Each risk as a card with severity badge.

```html
<div class="risk-card card fade-in-up">
  <div class="risk-header">
    <h4>风险名称</h4>
    <div class="risk-badges">
      <span class="badge badge-red">影响：高 🔴</span>
      <span class="badge badge-green">概率：低</span>
    </div>
  </div>
  <p class="risk-mitigation">
    <strong>缓解：</strong>具体应对措施...
  </p>
</div>
```

---

## 12. Navigation Bar

```html
<nav class="navbar" id="navbar">
  <div class="nav-progress" id="navProgress"></div>
  <div class="nav-inner">
    <div class="nav-brand">LOGO / TITLE</div>
    <div class="nav-links" id="navLinks">
      <a href="#section1" class="nav-link">Section 1</a>
      <a href="#section2" class="nav-link">Section 2</a>
      <!-- ... -->
      <button class="nav-glossary-btn" id="glossaryBtn">术语表</button>
    </div>
    <button class="hamburger" id="hamburger">☰</button>
  </div>
</nav>
```

```css
.navbar {
  position: fixed; top: 0; left: 0; right: 0;
  z-index: 999;
  background: rgba(10,15,28,0.8);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-subtle);
}
.nav-progress {
  height: 2px;
  background: var(--gradient-heading);
  width: 0%;
  transition: width 0.1s;
}
```

Scroll progress JS:
```javascript
window.addEventListener('scroll', () => {
  const scrollTop = document.documentElement.scrollTop;
  const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
  const progress = (scrollTop / scrollHeight) * 100;
  document.getElementById('navProgress').style.width = progress + '%';
});
```

---

## 13. Back-to-Top Button

```html
<button class="back-to-top" id="backToTop">↑</button>
```

```css
.back-to-top {
  position: fixed; bottom: 2rem; right: 2rem;
  width: 48px; height: 48px;
  border-radius: 50%;
  background: var(--accent-blue);
  color: white; border: none; cursor: pointer;
  opacity: 0; transform: scale(0.8);
  transition: opacity 0.3s, transform 0.3s;
  z-index: 998;
}
.back-to-top.visible {
  opacity: 1; transform: scale(1);
}
```

Show when `scrollY > window.innerHeight`.

---

## 14. Callout Box

See DESIGN-SYSTEM.md for the full pattern. Used for term explanations,
key insights, and important notes inline within sections.

---

## 15. Large Feature Cards (Moat / Strategic)

Like Feature Cards but larger, with gradient border effect:

```css
.moat-card {
  position: relative;
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 2.5rem;
}
.moat-card::before {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 17px;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan));
  z-index: -1;
  opacity: 0.3;
  transition: opacity 0.3s;
}
.moat-card:hover::before { opacity: 0.6; }
```
