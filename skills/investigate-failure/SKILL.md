---
name: investigate-failure
description: Systematic failure investigation. Use when errors appear, verify fails repeatedly, or unexpected behavior occurs.
user-invocable: "true"
---

# Investigate Failure

1. Check health (if in Immortal Agent project): `python3 -c "from src.harness.stethoscope import health_check; ..."`
2. Query recent errors: `python3 -c "from src.harness.query_dsl import query; query('status:error | last 10')"`
3. If no harness available: `grep -r "Error\|Exception\|Traceback" data/ --include="*.log" | tail -20`
4. Read relevant source files. Identify root cause. Fix.
5. Don't guess. QUERY. Data tells you what happened.
