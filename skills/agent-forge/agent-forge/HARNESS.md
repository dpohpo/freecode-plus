# Harness: agent-forge

## Design Philosophy
Harness is **telemetry, not a gate**. It measures quality and emits diagnostic events.
It never blocks execution. Failures are signals, not stop signs.

## Acceptance Criteria
- [x] Scout GitHub: returns formatted results (markdown or JSON) from API or offline fixture
- [x] Scout npm: returns formatted results from registry or offline fixture
- [x] Evaluate: scores candidates on 5 axes with numeric output (0-10 each) and total (0-50)
- [x] Evaluate: outputs decision recommendation (ADAPT/HYBRID/FORGE)
- [x] Forge skill: creates valid `SKILL.md` with correct frontmatter (name + description)
- [x] Forge skill: creates complete directory structure (SKILL.md, HARNESS.md, scripts/oracle.sh, tests/)
- [x] Forge skill: generated oracle.sh is executable and runs
- [x] Forge subagent: creates valid `.md` file with frontmatter (name, description, model, tools, memory)
- [x] Forge subagent: preset templates (planner/executor/critic) produce role-specific prompts
- [x] Register: emits `agent_registered` event to JSONL store (or reports "skipped" if no store)
- [x] All scripts: zero external dependencies (Python 3.8+ standard library only)
- [x] Offline: all scout commands work with `--offline-file` and local fixtures

## Oracle Test
Command: `bash scripts/oracle.sh`

Expected output pattern:
- Lines containing `[PASS]` or `[SKIP]` for each check
- Final line: `[PASS] agent-forge oracle complete`

Pass condition: Exit code 0

## Abort Conditions
- If `python3` is unavailable: ABORT — scripts require Python 3.8+
- If GitHub API returns 403 (rate limited): SKIP scout tests, continue with offline fixtures
- Maximum oracle runtime: 60 seconds

## Smoke Test
```bash
test -f ~/.claude/skills/agent-forge/SKILL.md && \
grep -q "name: agent-forge" ~/.claude/skills/agent-forge/SKILL.md && \
test -f ~/.claude/skills/agent-forge/HARNESS.md && \
test -d ~/.claude/skills/agent-forge/tests && \
test -f ~/.claude/skills/agent-forge/scripts/agent_forge.py && \
echo "[PASS] agent-forge smoke" || echo "[FAIL] agent-forge smoke"
```
