---
name: interactive-report
description: >
user-invocable: "true"
  Generate immersive, single-file interactive HTML reports with dark theme,
  scroll animations, and data visualizations. Use when the user asks to create
  a business plan report, pitch deck as HTML, interactive web presentation,
  data-driven narrative page, or any request involving converting a document/plan
  into a visually stunning single-page HTML experience. Also trigger when user
  mentions "报告", "商业计划", "interactive report", "HTML report", or
  "web presentation".
---

# Interactive HTML Report Generator

## Overview

This skill creates **immersive single-file HTML reports** — the kind that make
investors say "WOW" on first scroll. Think Apple product page + Stripe docs +
McKinsey report. All CSS and JS are inline, no external dependencies.

The user provides **report content** (business plan, analysis, data). This skill
provides the **design system, component library, and implementation patterns**.

## Workflow

1. **Analyze content**: Identify sections, key metrics, comparisons, timelines,
   and risk data from the user's input material.
2. **Map to components**: Each content type maps to a specific component from
   [COMPONENTS.md](COMPONENTS.md). Choose the best visual for each data type.
3. **Implement**: Build a single HTML file following [DESIGN-SYSTEM.md](DESIGN-SYSTEM.md)
   for all visual specs. Reference [EXAMPLE-STRUCTURE.md](EXAMPLE-STRUCTURE.md)
   for the canonical page skeleton.
4. **Validate**: Run through the checklist at the end of this file.

## Architecture Rules

- **Single file**: ALL CSS and JS inline. No external resources.
- **System fonts only**: `"PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", system-ui, sans-serif`
- **Vanilla only**: No React/Vue/jQuery. Modern CSS + Vanilla JS.
- **Dark theme primary**: `#0A0F1C` base. Full color spec in DESIGN-SYSTEM.md.
- **Responsive**: Desktop-first, but must work on mobile (hamburger nav, single-column grid, adjusted font sizes).
- **Content density management**: Use Accordion and Tab components to avoid infinite scrolling. Every section should feel "contained."

## Content → Component Mapping

| Content Type | Component | Notes |
|---|---|---|
| Key metrics / big numbers | Stat Cards (3-4 per row) | countUp animation on viewport entry |
| Feature list / advantages | Feature Cards | Icon + title + description, hover glow |
| SWOT analysis | SWOT Grid (2×2) | Four colors, hover zoom + glow |
| Competitive comparison | Comparison Table | Highlight "our" column |
| Technical architecture | Tab Component + diagrams | Multiple views via tabs |
| Phased roadmap | Vertical Timeline | Nodes light up on scroll |
| Cost/financial data | Progress Bars / Waterfall | Animated on entry |
| Risk assessment | Risk Cards with color coding | Red/Orange/Yellow severity |
| Moat / strategic advantages | Large Feature Cards | Gradient borders, icons |
| Action items / checklist | Checklist Cards | ✅/⬜ items |
| Glossary / terms | Accordion (sidebar drawer) | Collapsible definitions |

## Critical Implementation Details

### Intersection Observer Pattern
Every section and animated element uses ONE shared IntersectionObserver:
```javascript
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      // For countUp elements, trigger animation
      if (entry.target.dataset.countTarget) {
        animateCount(entry.target);
      }
      observer.unobserve(entry.target); // Fire once
    }
  });
}, { threshold: 0.15 });
```

### CountUp Animation
```javascript
function animateCount(el) {
  const target = parseFloat(el.dataset.countTarget);
  const suffix = el.dataset.countSuffix || '';
  const prefix = el.dataset.countPrefix || '';
  const duration = 1500;
  const start = performance.now();
  function update(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
    el.textContent = prefix + Math.floor(target * eased).toLocaleString() + suffix;
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}
```

### Stagger Effect
Child elements get `transition-delay` based on index:
```css
.stagger-children > *:nth-child(1) { transition-delay: 0s; }
.stagger-children > *:nth-child(2) { transition-delay: 0.1s; }
.stagger-children > *:nth-child(3) { transition-delay: 0.2s; }
/* ... up to 8 */
```

### Navigation
- Fixed top bar with `backdrop-filter: blur(12px)`
- Active section highlight via scroll spy (IntersectionObserver on sections)
- 2px gradient progress bar at very top of page
- Mobile: hamburger menu toggle

## Language

- Primary language: **Chinese (中文)** for all content
- Technical terms keep English originals (API, MCP, SaaS, ACOS, etc.)
- Code comments in English

## Final Checklist

Before outputting, verify:
- [ ] Hero has animated gradient background + bounce arrow
- [ ] All key numbers have countUp animation
- [ ] Scroll-in animations have stagger effect on child elements
- [ ] SWOT grid has correct 4 colors + hover effects
- [ ] Comparison table highlights "our project" column
- [ ] Timeline nodes light up sequentially on scroll
- [ ] Nav is fixed with glassmorphism effect
- [ ] Scroll progress bar works
- [ ] Glossary drawer opens/closes
- [ ] Mobile responsive (hamburger, single column)
- [ ] Back-to-top button appears after first screen
- [ ] All card hovers: translateY(-4px) + shadow + border glow
- [ ] Total file size reasonable (aim < 80KB for the HTML)
- [ ] No external resource dependencies

## Output

Save the final HTML file and present it to the user. The file should be
immediately openable in any browser with full functionality.
