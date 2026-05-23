---
name: loop
description: Fused best-current multi-agent SLL skill. It preserves all discovered conflicting variants and routes to the strongest applicable source without dropping capabilities.
---

# Fused Skill: loop

This skill had multiple distinct versions across local agents. The canonical version keeps a unified entry point and preserves every source version under `variants/` so no source capability is discarded.

## Operating Rule

1. Start with the unified rules in this file.
2. If the task clearly matches one source variant, read that variant's `SKILL.md` or `skill.md` under `variants/` before acting.
3. If variants disagree, prefer the more specific workflow for the named tool or agent, while preserving safety constraints from every relevant variant.
4. If a variant includes scripts, templates, assets, or references, use the preserved files from that variant directory instead of retyping them.

## Primary Variant

- Agent: `codex`
- Source: `/Users/poincare/.codex/skills/loop`
- Digest: `511193133534d787cdcc9e02ba13c827010db11b8a872b3be9cd7476d60eb7bb`
- Description: Follow the local triad loopback protocol for Codex, OpenCode, and CCGLM/freeglm. Use when a message contains $loop, /loop, TRIAD_LOOPBACK_V1, or asks agents to report to the next agent until the task is closed.

## Variant Map

| Agent | Digest | Files | Source | Preserved Variant | Description |
| --- | --- | ---: | --- | --- | --- |
| `codex` | `511193133534` | 2 | `/Users/poincare/.codex/skills/loop` | `variants/codex__511193133534` | Follow the local triad loopback protocol for Codex, OpenCode, and CCGLM/freeglm. Use when a message contains $loop, /loop, TRIAD_LOOPBACK_V1, or asks agents to report to the next agent until the task is closed. |
| `opencode` | `3c3247e3f93b` | 1 | `/Users/poincare/.config/opencode/skills/loop` | `variants/opencode__3c3247e3f93b` | Follow the local triad loopback protocol for Codex, OpenCode, and CCGLM/freeglm. Use when a message contains $loop, /loop, TRIAD_LOOPBACK_V1, or asks agents to report to the next agent until the task is closed. |

## Fused Capability Contract

- The canonical skill must cover all core abilities present in the listed variants.
- Do not remove a source-specific safety rule just because another variant omits it.
- Do not invent tool capability. Use the scripts and references actually preserved in the matching variant.
- When a source variant is stronger for a named ecosystem, route to that variant explicitly and cite the variant path in any handoff.
