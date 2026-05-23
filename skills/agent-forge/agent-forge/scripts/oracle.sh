#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

ok()   { echo "[PASS] $*"; }
fail() { echo "[FAIL] $*" >&2; EXIT_CODE=1; }
skip() { echo "[SKIP] $*"; }
EXIT_CODE=0

echo "=== Agent Forge Oracle ==="

# --- Structure ---
test -f "$ROOT/SKILL.md"   && ok "SKILL.md exists"   || fail "Missing SKILL.md"
test -f "$ROOT/HARNESS.md" && ok "HARNESS.md exists"  || fail "Missing HARNESS.md"
test -d "$ROOT/tests"      && ok "tests/ exists"      || fail "Missing tests/"
test -d "$ROOT/scripts"    && ok "scripts/ exists"     || fail "Missing scripts/"
test -d "$ROOT/references" && ok "references/ exists"  || fail "Missing references/"
test -f "$ROOT/scripts/agent_forge.py" && ok "agent_forge.py exists" || fail "Missing agent_forge.py"

# --- Frontmatter ---
grep -q "^name: agent-forge" "$ROOT/SKILL.md" && ok "SKILL.md name" || fail "SKILL.md missing name"
grep -q "^description: " "$ROOT/SKILL.md"     && ok "SKILL.md desc" || fail "SKILL.md missing description"

# --- Word count ---
cd "$ROOT"
WORDS=$(python3 -c "import re,pathlib; print(len(re.findall(r'\b\w+\b', pathlib.Path('SKILL.md').read_text())))")
[ "$WORDS" -le 5000 ] && ok "wordcount: $WORDS (<= 5000)" || fail "SKILL.md too long: $WORDS"

# --- Unit tests ---
if ! command -v python3 >/dev/null 2>&1; then
    fail "python3 not found"
    exit 1
fi

echo ""
echo "--- Running unit tests ---"
if python3 -m unittest discover -s "$ROOT/tests" -p "test_*.py" -v 2>&1; then
    ok "unit tests passed"
else
    fail "unit tests failed"
fi

# --- Integration: offline scout ---
echo ""
echo "--- Integration: offline scout ---"
SCOUT_OUT=$(python3 "$ROOT/scripts/agent_forge.py" scout github "test" --offline-file "$ROOT/tests/fixtures/github_search.json" --format json 2>&1) && {
    echo "$SCOUT_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); assert len(d)>0" 2>/dev/null \
        && ok "offline github scout" || fail "offline github scout returned empty"
} || fail "offline github scout error"

NPM_OUT=$(python3 "$ROOT/scripts/agent_forge.py" scout npm "test" --offline-file "$ROOT/tests/fixtures/npm_search.json" --format json 2>&1) && {
    echo "$NPM_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); assert len(d)>0" 2>/dev/null \
        && ok "offline npm scout" || fail "offline npm scout returned empty"
} || fail "offline npm scout error"

# --- Integration: evaluate ---
echo ""
echo "--- Integration: evaluate ---"
EVAL_OUT=$(python3 "$ROOT/scripts/agent_forge.py" scout github "test" --offline-file "$ROOT/tests/fixtures/github_search.json" --format json \
    | python3 "$ROOT/scripts/agent_forge.py" evaluate --capability "mcp orchestrate" --input - --format json 2>&1) && {
    echo "$EVAL_OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); assert all('score' in x for x in d)" 2>/dev/null \
        && ok "evaluate pipeline" || fail "evaluate missing scores"
} || fail "evaluate pipeline error"

# --- Integration: forge skill ---
echo ""
echo "--- Integration: forge skill ---"
TMPDIR=$(mktemp -d)
python3 "$ROOT/scripts/agent_forge.py" forge skill --name "test-skill" --description "A test skill" --output "$TMPDIR" >/dev/null 2>&1 && {
    test -f "$TMPDIR/test-skill/SKILL.md" && test -f "$TMPDIR/test-skill/HARNESS.md" && test -d "$TMPDIR/test-skill/tests" \
        && ok "forge skill" || fail "forge skill missing files"
} || fail "forge skill error"
rm -rf "$TMPDIR"

# --- Integration: forge subagent ---
echo ""
echo "--- Integration: forge subagent ---"
TMPDIR2=$(mktemp -d)
python3 "$ROOT/scripts/agent_forge.py" forge subagent --name "test-agent" --description "A test agent" --output "$TMPDIR2" --preset executor >/dev/null 2>&1 && {
    test -f "$TMPDIR2/test-agent.md" \
        && grep -q "model: sonnet" "$TMPDIR2/test-agent.md" \
        && ok "forge subagent (preset)" || fail "forge subagent missing content"
} || fail "forge subagent error"
rm -rf "$TMPDIR2"

# --- Integration: register (no event store) ---
echo ""
echo "--- Integration: register ---"
REG_OUT=$(python3 "$ROOT/scripts/agent_forge.py" register --name "test" --kind skill --path "/tmp/test" --event-store "/tmp/nonexistent-store.jsonl" 2>&1) && {
    echo "$REG_OUT" | grep -q '"skipped"' && ok "register (no store = skipped)" || fail "register unexpected output"
} || fail "register error"

# --- Summary ---
echo ""
if [ "$EXIT_CODE" -eq 0 ]; then
    ok "agent-forge oracle complete"
else
    fail "agent-forge oracle found errors"
fi
exit $EXIT_CODE
