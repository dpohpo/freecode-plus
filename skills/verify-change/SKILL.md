---
name: verify-change
description: Self-verification after code changes. Use after creating or editing any code. Runs syntax, lint, imports, tests. Mandatory, not optional.
user-invocable: "true"
---

# Verify Change

After EVERY code change:
1. Run project verify script: `bash scripts/verify.sh` (if exists in current project)
2. If no project script: `python3 -m py_compile <file> && ruff check <file>`
3. If fails → read teaching error message → fix → re-run. Max 3 loops.
4. If stuck 3 times → use harness-doctor agent.
