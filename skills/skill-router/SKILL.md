---
name: skill-router
description: Route each task to the right local skill combination. Use at session start and before work begins to classify the task, search available skills, and load the smallest useful set.
user-invocable: false
---

# Skill Router

Use this skill at the start of every new task.
Its job is to prevent memory drift by forcing explicit skill selection before execution.

## Wake-Up Protocol

When a new task arrives:

1. Read `skill-catalog` first.
2. Classify the task into one or more shapes:
   - browser chat operation
   - code edit
   - failure investigation
   - knowledge search
   - capability creation
   - multi-agent coordination
3. Pick the smallest skill set that covers all required shapes.
4. If no obvious match exists, search `~/.claude/skills/` before improvising.
5. Then start the actual work.

## Default Routing Table

- Browser chat, tab control, markdown export -> `browser-mcp-operator`
- Any code edit -> `verify-change`
- Any broken behavior or failing test -> `investigate-failure`
- Search for prior knowledge, historical notes, or mixed retrieval -> `searchin`
- Need a new skill, agent, or automation -> `agent-forge`
- Need cross-agent coordination or shared task state -> `blackboard`

## Search Procedure

If the route is still unclear:

1. Search `~/.claude/skills/**/SKILL.md`
2. Search `~/.claude/skills/**/skill.md`
3. Match by trigger words in frontmatter `description`
4. Read only the top 1-3 candidates
5. Prefer reuse over reinvention

## Hard Constraints

- Never assume a slash command is enough if a proper default skill exists.
- Never skip skill selection just because you vaguely remember a capability.
- Never load a giant pile of skills when 1-2 precise ones are enough.

## Common Routes

- Browser chat task -> `browser-mcp-operator`
- Browser chat task with follow-up coding -> `browser-mcp-operator` + `verify-change`
- Bugfix with unclear cause -> `investigate-failure` + `verify-change`
- New project protocol or agent setup -> `agent-forge` + `skill-catalog`
- Large ambiguous task -> `skill-catalog` + `skill-router`, then refine

## Additional Resources

- For the curated skill list, see [../skill-catalog/SKILL.md](../skill-catalog/SKILL.md).
- For common pairings, see [../skill-catalog/combos.md](../skill-catalog/combos.md).
