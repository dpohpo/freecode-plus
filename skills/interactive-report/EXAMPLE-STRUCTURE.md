# Example Page Structure

This is the canonical HTML skeleton. Adapt sections based on the user's content.
Not all sections are required — include only those that map to the user's data.

## Canonical Section Order

```
1. Hero Section          — Always first. Full viewport.
2. Key Metrics           — Stat Cards. Hook the reader with numbers.
3. Value Proposition     — Feature Cards. Why this matters.
4. Strategic Analysis    — SWOT Grid or similar framework.
5. Competitive Landscape — Comparison Table.
6. Architecture/How      — Tab Component for technical details.
7. Roadmap/Timeline      — Vertical Timeline with phases.
8. Financial Model       — Progress Bars + Stat Cards for breakeven.
9. Risk Assessment       — Risk Cards with severity badges.
10. Strategic Moat       — Large Feature Cards.
11. Call to Action       — Checklist cards, next steps.
12. Footer               — Quote + confidentiality notice.
13. Glossary Drawer      — Side panel, always accessible from nav.
```

## HTML Skeleton

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>报告标题</title>
  <style>
    /* === CSS Variables === */
    :root { /* ... from DESIGN-SYSTEM.md ... */ }

    /* === Reset & Base === */
    *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body { /* ... */ }

    /* === Navigation === */
    /* === Hero === */
    /* === Animations === */
    /* === Components === */
    /* === Responsive === */
  </style>
</head>
<body>
  <!-- Navigation -->
  <nav class="navbar" id="navbar">...</nav>

  <!-- Hero -->
  <section id="hero" class="hero">...</section>

  <!-- Content Sections -->
  <section id="metrics" class="section">...</section>
  <section id="value" class="section">...</section>
  <!-- ... more sections ... -->

  <!-- Footer -->
  <footer class="footer">...</footer>

  <!-- Glossary Drawer -->
  <div class="drawer-overlay" id="glossaryOverlay"></div>
  <aside class="drawer" id="glossaryDrawer">...</aside>

  <!-- Back to Top -->
  <button class="back-to-top" id="backToTop">↑</button>

  <script>
    // === Intersection Observer (scroll animations + countUp) ===
    // === Scroll Progress Bar ===
    // === Navigation: scroll spy + hamburger + glossary toggle ===
    // === Tab switching ===
    // === Accordion ===
    // === Back to top ===
  </script>
</body>
</html>
```

## Section Template Pattern

Every section follows this pattern:

```html
<section id="sectionId" class="section">
  <div class="container">
    <div class="section-header fade-in-up">
      <h2 class="section-title">标题</h2>
      <p class="section-subtitle">副标题</p>
    </div>

    <!-- Optional callout -->
    <div class="callout fade-in-up">
      <span class="callout-icon">💡</span>
      <div class="callout-content">说明文字</div>
    </div>

    <!-- Section body: cards, table, timeline, etc. -->
    <div class="grid-3 stagger-children">
      <div class="card fade-in-up">...</div>
      <div class="card fade-in-up">...</div>
      <div class="card fade-in-up">...</div>
    </div>
  </div>
</section>
```

## Adaptation Guidelines

When the user provides content that doesn't perfectly match the canonical order:

- **No SWOT data?** Skip Section 4.
- **No competitors?** Skip Comparison Table, perhaps use Feature Cards instead.
- **No timeline?** Use a simpler numbered list in cards.
- **Multiple technical topics?** Add more tabs to the Tab Component.
- **Very long content?** Aggressively use Accordions within sections.
- **Non-business content (research paper, tech doc)?** Replace Hero badges with
  metadata (authors, date, version). Replace SWOT with methodology. Replace
  financial model with results/findings.

The skill is content-agnostic — the design system and components work for any
type of long-form narrative that benefits from visual storytelling.
