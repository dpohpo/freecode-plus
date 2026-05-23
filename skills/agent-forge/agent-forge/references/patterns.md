# Agent Patterns Reference

Starting points for Scout. Always verify before installing.

## Skill Directory Structure

```
.claude/skills/{name}/
├── SKILL.md          # Required: frontmatter (name + description) + instructions
├── HARNESS.md        # Required: acceptance criteria + oracle + abort
├── scripts/          # Optional: executable code (oracle.sh lives here)
├── references/       # Optional: docs loaded into context as needed
├── assets/           # Optional: templates, images, configs
└── tests/            # Required: minimum 3 runnable tests
```

## Subagent File Format

```
.claude/agents/{name}.md
---
name: {kebab-case}
description: {trigger description}
model: {sonnet|opus|haiku|inherit}
tools: {comma-separated tool list}
memory: {user|project|local}
---
{system prompt}
```

## Core Triad (Planner/Executor/Critic)

| Role | Model | Tools | Purpose |
|------|-------|-------|---------|
| Planner | opus | Read, Grep, Glob, WebSearch | Decompose goals, create task lists |
| Executor | sonnet | Read, Write, Edit, Bash, Grep, Glob, MCP | Implement solutions, full access |
| Critic | opus | Read, Grep, Glob, Bash | Verify quality, run harness, report |

## MCP Servers: Shortlist (cross-checked Feb 2025)

### Multi-Agent Orchestration
- **all-agents-mcp** (npm/npx) — Orchestrate Claude Code, Codex, Gemini CLI, Copilot CLI via one MCP server
- **pal-mcp-server** (uvx/git) — Multi-model orchestration + conversation continuity across tools/models

### Core Dev Integrations
- **github-mcp-server** — GitHub official MCP server (issues/PRs/repos)
- **@playwright/mcp** (npm) — Official Playwright browser automation MCP
- **mcp-playwright** — Community Playwright MCP server
- **@anthropics/claude-code** — Claude Code as npm package (programmable)

### Data / Storage
- **@berthojoris/mcp-sqlite-server** — Secure SQLite MCP server
- **mcp-sqlite** — SQLite MCP server (community)

### Communication
- **slack-mcp** (npm) — Slack Web API via MCP
- **slack-mcp-server** (GitHub) — Full-featured Slack MCP server

### Official Anthropic Skills
- **skill-creator** — Create/iterate skills (meta-skill, no auto-test)
- **frontend-design** — Production-grade UI creation
- **webapp-testing** — Playwright-based web app testing
- **mcp-server** — Guide for creating MCP servers
- **docx, pdf, pptx, xlsx** — Document creation skills

### Autonomous Loop Tools
- **ralph-wiggum** — Claude Code plugin: Stop-hook loop with `--max-iterations` safety
- **Claude Code hooks** — 14 lifecycle events for custom automation
- **Auto-Claude** — Autonomous multi-agent framework with Kanban UI

## Harness Design Checklist

- [ ] Every test has explicit `[PASS]`/`[FAIL]`/`[SKIP]` output
- [ ] Errors on same line as `[FAIL]` (for grep)
- [ ] Total output < 50 lines (details to log file)
- [ ] At least 3 tests: structure, edge case, integration
- [ ] Oracle command is a single `bash` one-liner
- [ ] Oracle is telemetry — logs results, never blocks execution
- [ ] Abort conditions defined with maximum runtime

## Decision Rubric (Evaluate Output)

| Score Range | Decision | Action |
|-------------|----------|--------|
| >= 35/50 | ADAPT | Use directly, adapt if needed |
| 20-34 | HYBRID | Use as reference, build custom |
| < 20 | FORGE | Build from scratch |
