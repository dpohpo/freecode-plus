---
name: skill-catalog
description: Curated index of high-value local skills and when to use them. Use at session start, when choosing tools for a task, or when asked what skills are available.
user-invocable: false
---

# Skill Catalog

This skill is the fast local index for the most important skills in this environment.
Use it at the start of a task to avoid reinventing capabilities that already exist.

## Core Rule

Treat `~/.claude/skills/` as the canonical local capability registry.
Do not assume you remember the available skills correctly.

## High-Value Skills

- `skill-router`: choose the smallest relevant skill set for the current task and search for missing matches.
- `browser-mcp-operator`: operate logged-in Claude and ChatGPT web tabs through Brain MCP with low drift.
- `verify-change`: mandatory self-verification after code edits.
- `investigate-failure`: structured failure analysis when tests, commands, or systems fail.
- `searchin`: hybrid local search when you need to find prior knowledge or historical context.
- `agent-forge`: create, evaluate, and register new skills, agents, or capability scaffolds.
- `blackboard`: coordinate task flow through shared state when the work involves multiple agents.
- `long-running`: use for tasks that need durable looping, waiting, or background progress checks.

## First-Pass Matching

- Browser chat operation or artifact export -> `browser-mcp-operator`
- New code written or existing code edited -> `verify-change`
- Something broke and root cause is not obvious -> `investigate-failure`
- Need local knowledge recall or mixed retrieval -> `searchin`
- Need to create a new agent, skill, or automation pattern -> `agent-forge`
- Need to choose multiple skills for one task -> `skill-router`

## Search Policy

If the needed capability is not covered above:

1. Search `~/.claude/skills/**/SKILL.md` and `~/.claude/skills/**/skill.md`
2. Read only the most relevant candidates
3. Prefer the smallest skill set that fully covers the task

## Additional Resources

- For task-to-skill combinations, see [combos.md](combos.md).
- For the search protocol and wake-up flow, use [../skill-router/SKILL.md](../skill-router/SKILL.md).
