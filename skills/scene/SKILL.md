# /scene - Amazon Product Scene Prompt Generator

## Overview

Generate vivid, marketable scene prompts for Amazon main images (1600x1600px). Optimized for US/EU markets with soft-selling, natural product integration.

## Usage

```
/scene [product1], [product2], [product3], ...
```

**Output:**
- Image saved to: `~/Desktop/亚马逊作图/[产品1+产品2+产品3].png`
- Full prompt provided for copying to Midjourney/DALL-E/SD

**Examples:**
- `/scene beach, sunglasses, sunscreen` → A lifestyle shot with products naturally integrated
- `/scene yoga mat, water bottle, towel` → Fitness scene with soft product placement
- `/scene coffee mug, laptop, notebook` → Cozy workspace setup

## Design Principles

### 1. Style Matching (Auto-Select)
| Product Category | Visual Style |
|-----------------|--------------|
| Beach/Outdoor | California lifestyle - warm lighting, diverse models, action shots |
| Home/Kitchen | Minimalist Nordic - clean, bright, organized spaces |
| Beauty/Luxury | Premium elegant - sophisticated, carefully composed, rich textures |
| Fitness/Tech | Modern dynamic - active, authentic, relatable scenarios |

### 2. Model Selection (Product-Matched)
| Product Type | Typical Model |
|-------------|---------------|
| Makeup/Skincare | Women 25-40, diverse skin tones, radiant complexion |
| Fitness gear | Athletic builds, action poses, sweaty/effortless look |
| Tech accessories | Professionals, focused expressions, modern settings |
| Family products | Diverse ages, warm interactions, candid moments |

### 3. Soft-Selling Framework
- **70% scene / 30% product** - Products feel naturally present, not forced
- **Context first** - Show the lifestyle, then reveal the product
- **Authentic moments** - Capture genuine interactions, not posed shots
- **Environmental storytelling** - Setting suggests the product's value

### 4. Amazon Main Image Specs
- **Size**: 1600x1600px (1:1 square)
- **Format**: Prompt must include `--aspect_ratio 1:1` flag for Gemini
- **Style**: Product photography quality, professional lighting
- **Background**: Clean but contextual, no clutter

## Prompt Structure Template

```
[Scene description with natural lighting and environment],
[subject doing authentic action],
[products softly integrated into scene],
[photography style and technical details],
[diversity and lifestyle elements]
```

## Gemini CLI Command Format

```bash
gemini -p "A [scene]..." --image
# Output will be saved to current directory
```

## Examples

### Beach Bundle
**Input:** `/scene beach, sunglasses, sunscreen`

**Output Prompt:**
```
A candid lifestyle photo of a diverse group of friends enjoying a perfect Malibu beach day at golden hour. Warm California sunlight filtering through palm fronds. In the foreground, stylish premium sunglasses rest on a woven beach bag beside a luxury sunscreen bottle with elegant minimal packaging. The products appear naturally placed - as if someone just set them down before running into the waves. Shot in National Geographic travel style with shallow depth of field. Authentic moment, real people, genuine joy. 35mm film aesthetic, warm color palette. Professional product photography quality.

--aspect_ratio 1:1
```

### Yoga Bundle
**Input:** `/scene yoga mat, foam roller, water bottle`

**Output Prompt:**
```
A serene morning yoga session in a sun-drenched Scandinavian studio with floor-to-ceiling windows. A toned woman in premium athleisure wear flows through warrior pose on an eco-friendly yoga mat in calming sage green. A matching foam roller and sleek insulated water bottle sit neatly on reclaimed wood flooring beside her. The space feels curated yet authentic - potted fiddle leaf fig, soft textiles, natural light at 45 degrees. Minimalist aesthetic with earth tones. Professional product photography with soft shadows, commercial quality.

--aspect_ratio 1:1
```

### Home Office Bundle
**Input:** `/scene desk lamp, notebook, pen set`

**Output Prompt:**
```
An inviting modern workspace bathed in soft morning light from a large window. A brass desk lamp with warm LED glow illuminates a premium leather notebook lying open beside a set of German-engineered pens on a light oak desk. A cup of coffee steams nearby. The scene suggests creativity and focus - not staged, but a lived-in elegant workspace. Interior design magazine aesthetic, neutral color palette with brass accents. Professional product photography, sharp focus on products with bokeh background.

--aspect_ratio 1:1
```

## Style Keywords Bank

### Lighting
- Golden hour, natural window light, soft diffused lighting, backlit, dramatic shadows, ambient glow, sunrise, sunset, overcast soft light

### Environment
- Minimalist studio, boho-chic living room, modern loft, coastal patio, scandi bedroom, industrial kitchen, rooftop terrace, zen garden, cozy café

### Photography Styles
- National Geographic travel, Kinfolk magazine, architectural digest, editorial portrait, product photography, lifestyle commercial, authentic candid, street photography aesthetic

### Model Actions
- Laughing genuinely, focused working, stretching mid-pose, sipping thoughtfully, reaching naturally, mid-conversation, candid moment, effortless ease

## Diversity Commitment

Prompts will include:
- Diverse skin tones and ethnicities
- Various ages (Gen Z to Boomers, product-appropriate)
- Different body types
- Gender inclusivity where relevant

## Command

```bash
/scene [comma-separated product keywords]
```

The skill will analyze product types, auto-select appropriate style/models, and generate an optimized prompt ready for Gemini CLI.

---

**Created:** 2026-02-23
**For:** Amazon US/EU product listings
**Target:** Gemini CLI image generation
