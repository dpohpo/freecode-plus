---
name: report-amz
description: Fused best-current multi-agent SLL skill. It preserves all discovered conflicting variants and routes to the strongest applicable source without dropping capabilities.
---

# Fused Skill: report-amz

This skill had multiple distinct versions across local agents. The canonical version keeps a unified entry point and preserves every source version under `variants/` so no source capability is discarded.

## Operating Rule

1. Start with the unified rules in this file.
2. If the task clearly matches one source variant, read that variant's `SKILL.md` or `skill.md` under `variants/` before acting.
3. If variants disagree, prefer the more specific workflow for the named tool or agent, while preserving safety constraints from every relevant variant.
4. If a variant includes scripts, templates, assets, or references, use the preserved files from that variant directory instead of retyping them.

## Primary Variant

- Agent: `codex`
- Source: `/Users/poincare/.agent-shared-skills/releases/20260523T023619Z/skills/report-amz`
- Digest: `c30a55a5b8ecc38c4d636aae3a1fcacfbb7af4f99b37f6d96326b4fca7e9c98f`
- Description: Builds Amazon research HTML reports by using jyamzon for every data-acquisition step and the US Summer Products Research 2026 frontend only for rendering. Use when the user says /report-amz, asks to combine /jyamzon crawler data with /us-summer-products-research-2026 HTML, or wants crawler-backed Amazon product reports without SellerSprite MCP.

## Variant Map

| Agent | Digest | Files | Source | Preserved Variant | Description |
| --- | --- | ---: | --- | --- | --- |
| `codex` | `c30a55a5b8ec` | 124 | `/Users/poincare/.agent-shared-skills/releases/20260523T023619Z/skills/report-amz` | `variants/codex__c30a55a5b8ec` | Builds Amazon research HTML reports by using jyamzon for every data-acquisition step and the US Summer Products Research 2026 frontend only for rendering. Use when the user says /report-amz, asks to combine /jyamzon crawler data with /us-summer-products-research-2026 HTML, or wants crawler-backed Amazon product reports without SellerSprite MCP. |
| `claude` | `820f291f3b3b` | 124 | `/Users/poincare/.claude/skills/report-amz` | `variants/claude__820f291f3b3b` | Builds Amazon research HTML reports by using jyamzon for every data-acquisition step and the US Summer Products Research 2026 frontend only for rendering. Use when the user says /report-amz, asks to combine /jyamzon crawler data with /us-summer-products-research-2026 HTML, or wants crawler-backed Amazon product reports without SellerSprite MCP. |
| `opencode` | `bda8fb2056e4` | 124 | `/Users/poincare/.config/opencode/skills/report-amz` | `variants/opencode__bda8fb2056e4` | Builds Amazon research HTML reports by using jyamzon for every data-acquisition step and the US Summer Products Research 2026 frontend only for rendering. Use when the user says /report-amz, asks to combine /jyamzon crawler data with /us-summer-products-research-2026 HTML, or wants crawler-backed Amazon product reports without SellerSprite MCP. |

## Fused Capability Contract

- The canonical skill must cover all core abilities present in the listed variants.
- Do not remove a source-specific safety rule just because another variant omits it.
- Do not invent tool capability. Use the scripts and references actually preserved in the matching variant.
- When a source variant is stronger for a named ecosystem, route to that variant explicitly and cite the variant path in any handoff.
