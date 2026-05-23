# Design System Reference

## Color Palette

All colors managed via CSS custom properties on `:root`:

```css
:root {
  /* Backgrounds */
  --bg-primary: #0A0F1C;
  --bg-secondary: #111827;
  --bg-tertiary: #1E293B;

  /* Accent Colors */
  --accent-blue: #3B82F6;
  --accent-cyan: #06B6D4;
  --accent-orange: #F59E0B;
  --accent-green: #10B981;
  --accent-red: #EF4444;
  --accent-purple: #8B5CF6;

  /* Text */
  --text-primary: #F1F5F9;
  --text-secondary: #94A3B8;
  --text-muted: #64748B;

  /* Borders & Effects */
  --border-subtle: rgba(255,255,255,0.06);
  --glow-blue: rgba(59,130,246,0.15);
  --glow-cyan: rgba(6,182,212,0.15);

  /* Gradients */
  --gradient-heading: linear-gradient(135deg, #3B82F6, #06B6D4);
  --gradient-hero-bg: linear-gradient(135deg, #0A0F1C 0%, #1a1a3e 50%, #0A0F1C 100%);

  /* Spacing */
  --section-padding: 100px 0;
  --card-padding: 2rem;
  --container-max: 1200px;
  --content-max: 720px;

  /* Transitions */
  --transition-fast: 0.2s ease;
  --transition-normal: 0.3s ease;
  --transition-slow: 0.6s ease-out;
}
```

## Typography

```css
body {
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
               "Noto Sans SC", system-ui, sans-serif;
  color: var(--text-primary);
  background: var(--bg-primary);
  line-height: 1.75;
  font-size: 1rem;
}

/* Heading hierarchy */
.section-title {
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 800;
  letter-spacing: -0.02em;
  background: var(--gradient-heading);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.section-subtitle {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-secondary);
}

/* Big stat numbers */
.stat-number {
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 800;
  background: var(--gradient-heading);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Reading body text */
.prose {
  max-width: var(--content-max);
  line-height: 1.75;
  color: var(--text-secondary);
}
```

## Animation Specs

### 1. Scroll-In (fadeInUp)
```css
.fade-in-up {
  opacity: 0;
  transform: translateY(40px);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}
.fade-in-up.visible {
  opacity: 1;
  transform: translateY(0);
}
```

### 2. Card Hover
```css
.card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  padding: var(--card-padding);
  transition: transform var(--transition-normal),
              box-shadow var(--transition-normal),
              border-color var(--transition-normal);
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.3);
  border-color: rgba(59,130,246,0.3);
}
```

### 3. Hero Background
```css
@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
.hero {
  background: linear-gradient(-45deg, #0A0F1C, #1a1a3e, #0d2137, #0A0F1C);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
}
```

### 4. Bounce Arrow
```css
@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0) translateX(-50%); }
  40% { transform: translateY(-12px) translateX(-50%); }
  60% { transform: translateY(-6px) translateX(-50%); }
}
.scroll-arrow {
  animation: bounce 2s infinite;
}
```

### 5. Timeline Node Activation
```css
.timeline-node {
  width: 16px; height: 16px;
  border-radius: 50%;
  background: var(--bg-tertiary);
  border: 2px solid var(--text-muted);
  transition: all 0.5s ease;
}
.timeline-node.active {
  background: var(--accent-blue);
  border-color: var(--accent-cyan);
  box-shadow: 0 0 20px var(--glow-blue);
}
```

### 6. Progress Bar Fill
```css
.progress-fill {
  width: 0%;
  height: 8px;
  border-radius: 4px;
  background: var(--gradient-heading);
  transition: width 1.5s ease-out;
}
.progress-fill.visible {
  width: var(--target-width);
}
```

## Component Sizing (Responsive)

```css
/* Container */
.container {
  max-width: var(--container-max);
  margin: 0 auto;
  padding: 0 2rem;
}

/* Grid layouts */
.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }
.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; }

/* Mobile overrides */
@media (max-width: 768px) {
  :root {
    --section-padding: 60px 0;
    --card-padding: 1.5rem;
  }
  .grid-2, .grid-3, .grid-4 {
    grid-template-columns: 1fr;
  }
  .section-title { font-size: 2rem; }
  .stat-number { font-size: 2.5rem; }
  /* Hamburger nav */
  .nav-links { display: none; }
  .nav-links.open { display: flex; flex-direction: column; }
  .hamburger { display: block; }
}
@media (min-width: 769px) {
  .hamburger { display: none; }
}
```

## SWOT Color Mapping

| Quadrant | Color Variable | Background (10% opacity) |
|----------|---------------|-------------------------|
| Strengths | --accent-green (#10B981) | rgba(16,185,129,0.1) |
| Weaknesses | --accent-red (#EF4444) | rgba(239,68,68,0.1) |
| Opportunities | --accent-blue (#3B82F6) | rgba(59,130,246,0.1) |
| Threats | --accent-orange (#F59E0B) | rgba(245,158,11,0.1) |

## Risk Severity Colors

| Level | Color | Badge Style |
|-------|-------|------------|
| High (高) | --accent-red | `background: rgba(239,68,68,0.15); color: #EF4444;` |
| Medium (中) | --accent-orange | `background: rgba(245,158,11,0.15); color: #F59E0B;` |
| Low (低) | --accent-green | `background: rgba(16,185,129,0.15); color: #10B981;` |

## Callout Box Pattern

```html
<div class="callout">
  <span class="callout-icon">💡</span>
  <div class="callout-content">
    <strong>术语解释：</strong> Content here...
  </div>
</div>
```
```css
.callout {
  display: flex; gap: 1rem; align-items: flex-start;
  padding: 1.25rem 1.5rem;
  background: var(--bg-tertiary);
  border-left: 3px solid var(--accent-blue);
  border-radius: 0 8px 8px 0;
  margin: 1.5rem 0;
}
```
