#!/usr/bin/env python3
"""
Agent Forge v1.0 — Zero-dependency CLI for the Immortal Agent ecosystem.

Commands:
  scout github <query>        Search GitHub repos
  scout npm <query>           Search npm packages
  evaluate                    Score candidates on 5-axis rubric (0-10 each, 50 max)
  forge skill                 Generate a Claude Code Skill scaffold
  forge subagent              Generate a Claude Code Subagent scaffold
  register                    Emit agent_registered event to Immortal Agent event store

Design:
  - Standard library only (no requests, no jq, no pip install)
  - Offline-capable (--offline-file for all scout commands)
  - Machine-readable (JSON) + human-friendly (Markdown tables)
  - Safe-by-default (no installs, no destructive ops, --force required for overwrites)
  - Event store integration for Immortal Agent coordination
  - Harness = telemetry, not gate. Never blocks execution.
  - No capability restrictions on forged agents.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import stat
import sys
import textwrap
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ============================================================
# Utilities
# ============================================================

def _utc_now() -> _dt.datetime:
    return _dt.datetime.now(tz=_dt.timezone.utc)

def _utc_now_iso() -> str:
    return _utc_now().isoformat(timespec="seconds")

def _parse_iso(s: str) -> Optional[_dt.datetime]:
    if not s:
        return None
    try:
        return _dt.datetime.fromisoformat(s.replace("Z", "+00:00") if s.endswith("Z") else s)
    except Exception:
        return None

def _days_since(iso_str: str) -> Optional[int]:
    ts = _parse_iso(iso_str)
    if ts is None:
        return None
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=_dt.timezone.utc)
    return max(0, int((_utc_now() - ts).total_seconds() // 86400))

def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", (text or "").lower())

def _keyword_overlap(need: str, haystack: str) -> float:
    need_set = set(_tokenize(need))
    hay_set = set(_tokenize(haystack))
    if not need_set:
        return 0.0
    return len(need_set & hay_set) / len(need_set)

def _http_get_json(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 20) -> Tuple[int, Dict[str, str], Any]:
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, "status", 200)
            resp_hdrs = {k.lower(): v for k, v in resp.headers.items()}
            body = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        status = e.code
        resp_hdrs = {k.lower(): v for k, v in e.headers.items()} if e.headers else {}
        body = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e.reason}") from e
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        data = {"_raw": body[:500]}
    return status, resp_hdrs, data

def _md_table(rows: List[Dict[str, Any]], columns: List[Tuple[str, str]]) -> str:
    lines = []
    lines.append("| " + " | ".join(h for _, h in columns) + " |")
    lines.append("| " + " | ".join("---" for _ in columns) + " |")
    for row in rows:
        cells = []
        for key, _ in columns:
            v = str(row.get(key, "") or "").replace("|", "\\|").replace("\n", " ").strip()
            cells.append(v)
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"

def _chmod_x(path: Path) -> None:
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

def _validate_kebab(name: str) -> None:
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
        raise ValueError(f"Name must be kebab-case (got: '{name}')")


# ============================================================
# Scout: GitHub
# ============================================================

def scout_github(query: str, max_results: int = 10, token: Optional[str] = None, offline_file: Optional[Path] = None) -> List[Dict[str, Any]]:
    if offline_file:
        data = json.loads(offline_file.read_text("utf-8"))
        items = data.get("items", data if isinstance(data, list) else [])
        return [_shape_gh(i) for i in items[:max_results]]

    headers = {"Accept": "application/vnd.github+json", "User-Agent": "agent-forge/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    params = {"q": query.strip(), "sort": "stars", "order": "desc", "per_page": str(min(max_results, 100))}
    url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode(params)
    status, hdrs, data = _http_get_json(url, headers=headers)

    if status == 403:
        remaining = hdrs.get("x-ratelimit-remaining", "?")
        raise RuntimeError(f"GitHub API 403 (rate-limit remaining={remaining}). Set GITHUB_TOKEN or use --offline-file.")
    if status >= 400:
        msg = data.get("message", "") if isinstance(data, dict) else ""
        raise RuntimeError(f"GitHub API HTTP {status}: {msg}")
    items = data.get("items", []) if isinstance(data, dict) else []
    return [_shape_gh(i) for i in items[:max_results]]

def _shape_gh(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "source": "github",
        "name": item.get("name", ""),
        "full_name": item.get("full_name", ""),
        "description": (item.get("description") or "").strip()[:200],
        "stars": int(item.get("stargazers_count") or 0),
        "updated_at": item.get("updated_at") or "",
        "url": item.get("html_url") or "",
        "language": item.get("language") or "",
        "license": (item.get("license") or {}).get("spdx_id", "") if isinstance(item.get("license"), dict) else "",
        "topics": item.get("topics", []),
    }


# ============================================================
# Scout: npm
# ============================================================

def scout_npm(query: str, max_results: int = 10, offline_file: Optional[Path] = None) -> List[Dict[str, Any]]:
    if offline_file:
        data = json.loads(offline_file.read_text("utf-8"))
        objects = data.get("objects", data if isinstance(data, list) else [])
        return [_shape_npm(o) for o in objects[:max_results]]

    params = {"text": query.strip(), "size": str(min(max_results, 250))}
    url = "https://registry.npmjs.org/-/v1/search?" + urllib.parse.urlencode(params)
    status, _, data = _http_get_json(url, headers={"User-Agent": "agent-forge/1.0"})
    if status >= 400:
        raise RuntimeError(f"npm registry HTTP {status}")
    objects = data.get("objects", []) if isinstance(data, dict) else []
    return [_shape_npm(o) for o in objects[:max_results]]

def _shape_npm(obj: Dict[str, Any]) -> Dict[str, Any]:
    pkg = obj.get("package", obj) if isinstance(obj, dict) else {}
    links = pkg.get("links", {}) if isinstance(pkg.get("links"), dict) else {}
    score_obj = obj.get("score", {}) if isinstance(obj, dict) else {}
    detail = score_obj.get("detail", {}) if isinstance(score_obj, dict) else {}
    popularity = detail.get("popularity", 0) if isinstance(detail, dict) else 0
    return {
        "source": "npm",
        "name": pkg.get("name", ""),
        "full_name": pkg.get("name", ""),
        "description": (pkg.get("description") or "").strip()[:200],
        "version": pkg.get("version", ""),
        "date": pkg.get("date", ""),
        "url": links.get("npm") or links.get("repository") or links.get("homepage") or "",
        "popularity": round(float(popularity), 4),
        "updated_at": pkg.get("date", ""),
    }


# ============================================================
# Evaluate: 5-axis scoring rubric
# ============================================================

@dataclass
class CandidateScore:
    fitness: int = 0
    freshness: int = 0
    maturity: int = 0
    integration: int = 0
    scope: int = 0

    @property
    def total(self) -> int:
        return self.fitness + self.freshness + self.maturity + self.integration + self.scope

    def to_dict(self) -> Dict[str, int]:
        return {"fitness": self.fitness, "freshness": self.freshness, "maturity": self.maturity,
                "integration": self.integration, "scope": self.scope, "total": self.total}

def _score_fitness(capability: str, name: str, desc: str) -> int:
    return min(10, int(round(_keyword_overlap(capability, f"{name} {desc}") * 10)))

def _score_freshness(updated_at: str) -> int:
    days = _days_since(updated_at)
    if days is None: return 0
    if days <= 14:  return 10
    if days <= 30:  return 9
    if days <= 90:  return 7
    if days <= 180: return 5
    if days <= 365: return 3
    return 1

def _score_maturity(candidate: Dict[str, Any]) -> int:
    if candidate.get("source") == "npm":
        pop = float(candidate.get("popularity", 0))
        if pop >= 0.8:  return 10
        if pop >= 0.5:  return 8
        if pop >= 0.2:  return 6
        if pop >= 0.05: return 4
        return 2
    stars = int(candidate.get("stars") or 0)
    if stars >= 10000: return 10
    if stars >= 5000:  return 9
    if stars >= 1000:  return 8
    if stars >= 500:   return 7
    if stars >= 100:   return 5
    if stars >= 30:    return 3
    if stars >= 5:     return 2
    return 1

_INTEGRATION_KW = [
    ("model context protocol", 3), ("mcp server", 3), ("mcp", 2),
    ("claude code", 3), ("claude-code", 3), ("claude", 1),
    ("codex cli", 2), ("gemini cli", 2), ("copilot cli", 2),
    ("stdio", 1), ("jsonrpc", 1), ("subagent", 2), ("hook", 1),
    ("plugin", 1), ("orchestrat", 2),
]

def _score_integration(name: str, desc: str, topics: List[str] = None) -> int:
    blob = f"{name} {desc} {' '.join(topics or [])}".lower()
    return min(10, sum(w for kw, w in _INTEGRATION_KW if kw in blob))

_BLOAT = ["all-in-one", "comprehensive", "full-featured", "platform", "enterprise",
          "framework", "everything", "end-to-end", "ultimate", "universal"]
_FOCUS = ["mcp", "server", "plugin", "cli", "stdio", "hook", "tool", "single"]

def _score_scope(desc: str) -> int:
    d = (desc or "").lower()
    return max(0, min(10, 6 + sum(1 for m in _FOCUS if m in d) - sum(2 for m in _BLOAT if m in d)))

def evaluate_candidates(candidates: List[Dict[str, Any]], capability: str) -> List[Dict[str, Any]]:
    results = []
    for c in candidates:
        name = c.get("full_name") or c.get("name") or ""
        desc = c.get("description") or ""
        updated = c.get("updated_at") or c.get("date") or ""
        topics = c.get("topics", [])
        score = CandidateScore(
            fitness=_score_fitness(capability, name, desc),
            freshness=_score_freshness(updated),
            maturity=_score_maturity(c),
            integration=_score_integration(name, desc, topics),
            scope=_score_scope(desc),
        )
        out = dict(c)
        out["score"] = score.to_dict()
        t = score.total
        out["decision"] = "ADAPT" if t >= 35 else ("HYBRID" if t >= 20 else "FORGE")
        results.append(out)
    results.sort(key=lambda x: x.get("score", {}).get("total", 0), reverse=True)
    return results


# ============================================================
# Forge: Skill scaffold
# ============================================================

_SKILL_TPL = textwrap.dedent("""\
    ---
    name: {name}
    description: {description}
    ---

    # {title}

    ## Purpose
    <!-- What this skill does, in 2-3 lines. -->

    ## When to trigger
    <!-- User phrases/contexts that activate this skill. Be specific and "pushy". -->

    ## Inputs
    <!-- What information/files/parameters does the agent need? -->

    ## Outputs
    <!-- What does success look like? What format? -->

    ## Workflow
    1. Validate inputs, clarify assumptions (max 1 question if critical)
    2. Execute the core task
    3. Run harness checks (telemetry — log results, do not block)
    4. Report results with clear status signals

    ## Examples
    ### Example 1
    Input: `/{name} ...`
    Expected: <!-- what success looks like -->
""")

_HARNESS_TPL = textwrap.dedent("""\
    # Harness: {name}

    ## Acceptance Criteria
    - [ ] TODO: Define 3-10 specific, measurable criteria
    - [ ] TODO: Each criterion must be verifiable by script or test
    - [ ] TODO: At least one integration/end-to-end criterion

    ## Oracle Test
    Command: `bash scripts/oracle.sh`
    Expected: All lines `[PASS]` or `[SKIP]`, none `[FAIL]`
    Pass condition: Exit code 0
    Note: Oracle is telemetry. Failures emit events but do not block execution.

    ## Abort Conditions
    - If `python3` unavailable: ABORT (scripts require Python 3.8+)
    - Maximum oracle runtime: 60 seconds

    ## Smoke Test
    ```bash
    test -f SKILL.md && test -f HARNESS.md && test -d tests && echo "[PASS] smoke" || echo "[FAIL] smoke"
    ```
""")

_ORACLE_TPL = textwrap.dedent("""\
    #!/usr/bin/env bash
    set -euo pipefail
    ROOT="$(cd "$(dirname "${{BASH_SOURCE[0]}}")/.." && pwd)"

    ok()   {{ echo "[PASS] $*"; }}
    fail() {{ echo "[FAIL] $*" >&2; EXIT_CODE=1; }}
    skip() {{ echo "[SKIP] $*"; }}
    EXIT_CODE=0

    test -f "$ROOT/SKILL.md"   && ok "SKILL.md exists"   || fail "Missing SKILL.md"
    test -f "$ROOT/HARNESS.md" && ok "HARNESS.md exists"  || fail "Missing HARNESS.md"
    test -d "$ROOT/tests"      && ok "tests/ exists"      || fail "Missing tests/"

    grep -q "^name: " "$ROOT/SKILL.md"        && ok "has name"        || fail "missing name"
    grep -q "^description: " "$ROOT/SKILL.md"  && ok "has description" || fail "missing description"

    cd "$ROOT"
    WORDS=$(python3 -c "import re,pathlib; print(len(re.findall(r'\\\\b\\\\w+\\\\b', pathlib.Path('SKILL.md').read_text())))")
    [ "$WORDS" -le 5000 ] && ok "wordcount: $WORDS" || fail "SKILL.md too long: $WORDS words"

    if compgen -G "$ROOT/tests/test_*.py" > /dev/null 2>&1; then
        python3 -m unittest discover -s "$ROOT/tests" -p "test_*.py" -v 2>&1 && ok "unit tests passed" || fail "unit tests failed"
    else
        skip "no test_*.py found"
    fi

    [ "$EXIT_CODE" -eq 0 ] && ok "{name} oracle complete" || fail "{name} oracle found errors"
    exit $EXIT_CODE
""")

_TEST_TPL = textwrap.dedent("""\
    import re
    import unittest
    from pathlib import Path

    SKILL_ROOT = Path(__file__).resolve().parents[1]


    class TestStructure(unittest.TestCase):
        def test_skill_md_exists(self):
            self.assertTrue((SKILL_ROOT / "SKILL.md").exists())

        def test_skill_md_frontmatter(self):
            text = (SKILL_ROOT / "SKILL.md").read_text()
            self.assertIn("name:", text)
            self.assertIn("description:", text)

        def test_harness_md_exists(self):
            self.assertTrue((SKILL_ROOT / "HARNESS.md").exists())

        def test_tests_directory(self):
            self.assertTrue((SKILL_ROOT / "tests").is_dir())

        def test_word_count(self):
            text = (SKILL_ROOT / "SKILL.md").read_text()
            words = len(re.findall(r"\\b\\w+\\b", text))
            self.assertLessEqual(words, 5000)


    class TestPlaceholders(unittest.TestCase):
        \"\"\"These FAIL until you write real tests. Intentional.\"\"\"
        def test_acceptance_1(self):
            self.fail("TODO: real acceptance test for '{name}'")
        def test_acceptance_2(self):
            self.fail("TODO: real acceptance test for '{name}'")
        def test_acceptance_3(self):
            self.fail("TODO: real acceptance test for '{name}'")


    if __name__ == "__main__":
        unittest.main()
""")


def forge_skill(name: str, description: str, out_dir: Path, force: bool = False) -> Path:
    _validate_kebab(name)
    if len(description) > 200:
        raise ValueError("description must be <= 200 characters")
    skill_dir = out_dir / name
    if skill_dir.exists() and not force:
        raise FileExistsError(f"Already exists: {skill_dir} (use --force)")
    skill_dir.mkdir(parents=True, exist_ok=True)
    for sub in ["scripts", "references", "tests", "assets"]:
        (skill_dir / sub).mkdir(exist_ok=True)
    ctx = {"name": name, "description": description, "title": name.replace("-", " ").title()}
    (skill_dir / "SKILL.md").write_text(_SKILL_TPL.format(**ctx))
    (skill_dir / "HARNESS.md").write_text(_HARNESS_TPL.format(**ctx))
    oracle = skill_dir / "scripts" / "oracle.sh"
    oracle.write_text(_ORACLE_TPL.format(**ctx))
    _chmod_x(oracle)
    (skill_dir / "tests" / f"test_{name.replace('-', '_')}.py").write_text(_TEST_TPL.format(**ctx))
    return skill_dir


# ============================================================
# Forge: Subagent scaffold
# ============================================================

# --- Preset templates for the Planner/Executor/Critic triad ---
_PRESETS: Dict[str, Dict[str, str]] = {
    "planner": {
        "model": "opus",
        "tools": "Read, Grep, Glob, WebSearch, Bash(read-only)",
        "prompt": textwrap.dedent("""\
            You are **{name}**, the strategic planning agent.

            # Mission
            Decompose complex goals into concrete, ordered task lists.
            For each task: define acceptance criteria, estimate complexity, identify dependencies.

            # Workflow
            1. Analyze the goal and gather context (read files, search if needed)
            2. Decompose into tasks with clear done-criteria
            3. Output a structured plan as JSON array of task objects
            4. Flag risks and unknowns explicitly

            # Output Format
            ```json
            [
              {{"id": "T1", "title": "...", "depends_on": [], "acceptance": "...", "complexity": "S|M|L|XL"}},
              ...
            ]
            ```"""),
    },
    "executor": {
        "model": "sonnet",
        "tools": "Read, Write, Edit, Bash, Grep, Glob, WebFetch, MCP",
        "prompt": textwrap.dedent("""\
            You are **{name}**, the execution agent.

            # Mission
            Take task specifications and deliver working implementations.
            You have full system access. Use it.

            # Workflow
            1. Read task spec and acceptance criteria
            2. Implement the solution (code, config, files, CLI commands — whatever it takes)
            3. Self-test: run any available tests or sanity checks
            4. Report: status + what you created/changed + any issues found

            # Output Format
            Start with status line: `[DONE]`, `[BLOCKED <reason>]`, or `[PARTIAL <what remains>]`
            Then list files changed/created."""),
    },
    "critic": {
        "model": "opus",
        "tools": "Read, Grep, Glob, Bash",
        "prompt": textwrap.dedent("""\
            You are **{name}**, the quality and verification agent.

            # Mission
            Verify that delivered work meets acceptance criteria.
            Run tests. Check edge cases. Find what others missed.

            # Workflow
            1. Read the task spec and acceptance criteria
            2. Read the implementation
            3. Run all available tests and harness checks
            4. Report verdict with evidence

            # Output Format
            ```
            VERDICT: PASS | FAIL | PARTIAL
            EVIDENCE:
            - [PASS] criterion 1: <proof>
            - [FAIL] criterion 2: <what's wrong>
            RECOMMENDATIONS:
            - <what to fix>
            ```"""),
    },
}

_SUBAGENT_TPL = textwrap.dedent("""\
    ---
    name: {name}
    description: {description}
    model: {model}
    tools: {tools}
    memory: {memory}
    ---

    {prompt}
""")


def forge_subagent(
    name: str, description: str, out_dir: Path,
    model: str = "sonnet", tools: str = "Read, Grep, Glob",
    memory: str = "project", prompt: str = "",
    preset: str = "", force: bool = False,
) -> Path:
    _validate_kebab(name)
    if len(description) > 200:
        raise ValueError("description must be <= 200 characters")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{name}.md"
    if path.exists() and not force:
        raise FileExistsError(f"Already exists: {path} (use --force)")

    # Apply preset if specified
    if preset and preset in _PRESETS:
        p = _PRESETS[preset]
        model = p.get("model", model)
        tools = p.get("tools", tools)
        prompt = p.get("prompt", "").format(name=name)

    if not prompt.strip():
        prompt = (f"You are **{name}**. Mission: {description}. "
                  f"Produce concise, actionable output. Prefer structured data over prose.")

    path.write_text(_SUBAGENT_TPL.format(
        name=name, description=description, model=model,
        tools=tools, memory=memory, prompt=prompt,
    ))
    return path


# ============================================================
# Register: Emit event to Immortal Agent event store
# ============================================================

def register_agent(name: str, kind: str, path: str, event_store: Path, metadata: Optional[Dict] = None) -> Dict[str, Any]:
    event = {
        "type": "agent_registered",
        "timestamp": _utc_now_iso(),
        "payload": {"agent_name": name, "agent_kind": kind, "path": str(path), "metadata": metadata or {}},
    }
    if not event_store.exists():
        return {"status": "skipped", "reason": f"Event store not found: {event_store}", "event": event}
    with open(event_store, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return {"status": "registered", "event": event}


# ============================================================
# CLI
# ============================================================

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="agent_forge", description="Agent Forge v1.0 — Scout, Evaluate, Forge, Register.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # scout
    scout_p = sub.add_parser("scout", help="Search GitHub or npm.")
    scout_sub = scout_p.add_subparsers(dest="where", required=True)
    gh_p = scout_sub.add_parser("github", help="Search GitHub repos.")
    gh_p.add_argument("query")
    gh_p.add_argument("--max-results", type=int, default=10)
    gh_p.add_argument("--format", choices=["json", "markdown"], default="json")
    gh_p.add_argument("--offline-file", default="")
    gh_p.add_argument("--token-env", default="GITHUB_TOKEN")
    npm_p = scout_sub.add_parser("npm", help="Search npm packages.")
    npm_p.add_argument("query")
    npm_p.add_argument("--max-results", type=int, default=10)
    npm_p.add_argument("--format", choices=["json", "markdown"], default="json")
    npm_p.add_argument("--offline-file", default="")

    # evaluate
    eval_p = sub.add_parser("evaluate", help="Score candidates on 5-axis rubric.")
    eval_p.add_argument("--capability", required=True)
    eval_p.add_argument("--input", required=True, help="Path to JSON or '-' for stdin.")
    eval_p.add_argument("--format", choices=["json", "markdown"], default="json")

    # forge
    forge_p = sub.add_parser("forge", help="Generate skill or subagent scaffold.")
    forge_sub = forge_p.add_subparsers(dest="kind", required=True)
    fs_p = forge_sub.add_parser("skill")
    fs_p.add_argument("--name", required=True)
    fs_p.add_argument("--description", required=True)
    fs_p.add_argument("--output", required=True)
    fs_p.add_argument("--force", action="store_true")
    fa_p = forge_sub.add_parser("subagent")
    fa_p.add_argument("--name", required=True)
    fa_p.add_argument("--description", required=True)
    fa_p.add_argument("--output", required=True)
    fa_p.add_argument("--model", default="sonnet")
    fa_p.add_argument("--tools", default="Read, Grep, Glob")
    fa_p.add_argument("--memory", default="project")
    fa_p.add_argument("--prompt", default="")
    fa_p.add_argument("--preset", default="", choices=["", "planner", "executor", "critic"])
    fa_p.add_argument("--force", action="store_true")

    # register
    reg_p = sub.add_parser("register", help="Emit agent_registered event.")
    reg_p.add_argument("--name", required=True)
    reg_p.add_argument("--kind", required=True, choices=["skill", "subagent"])
    reg_p.add_argument("--path", required=True)
    reg_p.add_argument("--event-store", required=True)

    args = parser.parse_args(argv)

    try:
        if args.cmd == "scout":
            offline = Path(args.offline_file) if args.offline_file else None
            if args.where == "github":
                token = os.environ.get(args.token_env, "") or None
                results = scout_github(args.query, args.max_results, token, offline)
                cols = [("full_name", "Repo"), ("stars", "★"), ("updated_at", "Updated"),
                        ("language", "Lang"), ("license", "License"), ("url", "URL"), ("description", "Description")]
            else:
                results = scout_npm(args.query, args.max_results, offline)
                cols = [("name", "Package"), ("version", "Ver"), ("date", "Date"),
                        ("popularity", "Pop"), ("url", "URL"), ("description", "Description")]
            print(json.dumps(results, indent=2, ensure_ascii=False) if args.format == "json" else _md_table(results, cols))
            return 0

        if args.cmd == "evaluate":
            candidates = json.loads(sys.stdin.read() if args.input == "-" else Path(args.input).read_text("utf-8"))
            if not isinstance(candidates, list):
                raise ValueError("Input must be a JSON array.")
            scored = evaluate_candidates(candidates, args.capability)
            if args.format == "json":
                print(json.dumps(scored, indent=2, ensure_ascii=False))
            else:
                rows = [{"name": c.get("full_name") or c.get("name"), **c.get("score", {}),
                         "decision": c.get("decision"), "url": c.get("url")} for c in scored]
                print(_md_table(rows, [("name", "Candidate"), ("total", "Total"), ("fitness", "Fit"),
                                       ("freshness", "Fresh"), ("maturity", "Mature"), ("integration", "Integ"),
                                       ("scope", "Scope"), ("decision", "Decision"), ("url", "URL")]))
                print("Decision: >=35 ADAPT | 20-34 HYBRID | <20 FORGE")
            return 0

        if args.cmd == "forge":
            if args.kind == "skill":
                r = forge_skill(args.name, args.description, Path(args.output).expanduser(), args.force)
                print(json.dumps({"forged": "skill", "path": str(r)}))
            else:
                r = forge_subagent(args.name, args.description, Path(args.output).expanduser(),
                                   model=args.model, tools=args.tools, memory=args.memory,
                                   prompt=args.prompt, preset=args.preset, force=args.force)
                print(json.dumps({"forged": "subagent", "path": str(r)}))
            return 0

        if args.cmd == "register":
            r = register_agent(args.name, args.kind, args.path, Path(args.event_store).expanduser())
            print(json.dumps(r, indent=2, ensure_ascii=False))
            return 0

    except FileExistsError as e:
        print(f"[FAIL] {e}", file=sys.stderr); return 3
    except ValueError as e:
        print(f"[FAIL] {e}", file=sys.stderr); return 2
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr); return 4
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}", file=sys.stderr); return 1

if __name__ == "__main__":
    raise SystemExit(main())
