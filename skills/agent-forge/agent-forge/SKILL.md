---
name: agent-forge
description: "Agent factory for discovering, evaluating, creating, and registering Claude Code skills and subagents. Use this skill whenever the user mentions creating agents, finding tools, searching GitHub/npm for MCP servers, scaffolding skills, generating subagents, evaluating candidate repos, or building any kind of automation pipeline. Also trigger when users say 'I need an agent that...', 'find a tool for...', 'search for...', 'create a skill', 'forge', or reference the Immortal Agent system. Even if the user just asks about available MCP servers or wants to set up a new capability, use this skill."
---

# Agent Forge

A meta-skill that turns Claude Code into an agent factory. Provides a disciplined pipeline: **Scout → Evaluate → Forge → Harness → Register**.

Every agent produced by this factory ships with tests and a harness. Harness is telemetry — it measures quality but never blocks execution.

## Core Principles

1. **Search before you build.** Scout is recommended (not mandatory). Even a quick search often reveals something usable.
2. **Every agent gets a harness.** No exceptions. But harness = telemetry, not gate.
3. **No capability restrictions.** Forged agents have full system access. Constraints are behavioral suggestions, not enforced limits.
4. **File-based persistence.** Everything lands in git. Models are replaceable; files are permanent.

## Workflow

### Step 1: Scout (recommended)

Search for existing solutions before building from scratch.

```bash
# GitHub
python3 scripts/agent_forge.py scout github "mcp orchestrator multi-model" --max-results 10 --format markdown

# npm
python3 scripts/agent_forge.py scout npm "slack mcp server" --max-results 10 --format markdown

# Offline (for testing or rate-limited environments)
python3 scripts/agent_forge.py scout github "query" --offline-file tests/fixtures/github_search.json
```

If you already know what to build, skip directly to Step 3.

### Step 2: Evaluate

Score candidates on 5 axes (0-10 each, 50 max):

| Axis | Measures |
|------|----------|
| Fitness | Keyword overlap with your need |
| Freshness | Days since last update |
| Maturity | Stars (GitHub) or popularity (npm) |
| Integration | Claude/MCP ecosystem signals |
| Scope | Focused tool vs bloated framework |

```bash
python3 scripts/agent_forge.py scout github "mcp sqlite" --format json \
  | python3 scripts/agent_forge.py evaluate --capability "sqlite mcp server" --input - --format markdown
```

Decision rules: **>=35 ADAPT** | **20-34 HYBRID** | **<20 FORGE**

### Step 3: Forge

Two agent types:

**Skills** — Complex capabilities with their own directory, tests, and harness:

```bash
python3 scripts/agent_forge.py forge skill \
  --name "db-migrator" \
  --description "Run and validate database migrations with rollback support" \
  --output ".claude/skills"
```

Creates:
```
.claude/skills/db-migrator/
├── SKILL.md          # Frontmatter + instructions
├── HARNESS.md        # Acceptance criteria + oracle
├── scripts/oracle.sh # One-command validation
├── references/       # Docs referenced by SKILL.md
├── assets/           # Templates, configs
└── tests/            # Structure tests + placeholder acceptance tests
```

**Subagents** — Lightweight role definitions for Claude Code agent teams:

```bash
python3 scripts/agent_forge.py forge subagent \
  --name "code-reviewer" \
  --description "Review code for security and correctness" \
  --output ".claude/agents" \
  --model opus \
  --tools "Read, Grep, Glob, Bash"
```

**Preset roles** for the Planner/Executor/Critic triad:

```bash
# Strategic planner (uses Opus for deep reasoning)
python3 scripts/agent_forge.py forge subagent --name "planner" \
  --description "Decompose goals into ordered task lists" \
  --output ".claude/agents" --preset planner

# Execution agent (uses Sonnet for speed, full tool access)
python3 scripts/agent_forge.py forge subagent --name "executor" \
  --description "Implement solutions with full system access" \
  --output ".claude/agents" --preset executor

# Quality verifier (uses Opus for thorough analysis)
python3 scripts/agent_forge.py forge subagent --name "critic" \
  --description "Verify work meets acceptance criteria" \
  --output ".claude/agents" --preset critic
```

### Step 4: Harness

Every forged skill comes with `HARNESS.md` and `scripts/oracle.sh`. Run:

```bash
bash .claude/skills/{name}/scripts/oracle.sh
```

Oracle outputs `[PASS]`, `[FAIL]`, or `[SKIP]` per check. Failures are diagnostic — they tell you what needs attention but don't prevent the agent from operating.

### Step 5: Register (optional)

If an Immortal Agent event store exists, register the new agent:

```bash
python3 scripts/agent_forge.py register \
  --name "db-migrator" --kind skill \
  --path ".claude/skills/db-migrator" \
  --event-store ".immortal-agent/events.jsonl"
```

If no event store exists, it reports "skipped" and continues.

## Anti-Patterns to Avoid

- **Creating agents without harness** — Even a minimal harness is better than none.
- **200 agents before 3 work** — Start with the Planner/Executor/Critic triad. Scale after they're solid.
- **Capability restrictions in templates** — Don't add "never do X" to agent prompts. Use behavioral suggestions instead.
- **Ignoring Scout results** — If something scores >=35, adapt it. Don't rebuild from scratch out of pride.

## Reference Files

- `references/patterns.md` — Known MCP servers, skill patterns, harness checklist
- `references/hooks.md` — Claude Code hook events and integration patterns
