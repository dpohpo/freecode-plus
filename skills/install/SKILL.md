---
name: install
description: <!-- ============================================================ --> - Poincare技能集
user-invocable: "true"
---

> **Anti-Hallucination Iron Laws (Global | See ~/.claude/CLAUDE.md)**
> 1.Honesty: say "I don't know" when you don't 2.Evidence-first: suspect until proven, self-verification invalid 3.98% threshold: no certainty below 98% confidence 4.Failure conditions required: every technical claim must state when it breaks 5.Code delivery: all external APIs/commands/configs must be verified real, mark UNVERIFIED if not | Exempt: only when user explicitly declares

> **Coding Iron Laws + Self-Audit (When code is involved | See /coding)**
> Iron Laws: scan before code | dual-track verify (network+execution) | trace to primary source | 98% for certainty | self-built features need triple verification | every build layer VERIFIED | failure conditions required | "doesn't exist" needs 3 rounds of proof
> Self-Audit: all external claims identified | all deps >=98% VERIFIED | no untagged external refs | all tech claims have validity/failure/verification triplet | never used "should work"

> **Self-Alignment Protocol (Global | Viral — all modes/skills must carry this)**
> Before each execution, self-check in 1 line: `[ALIGN] Mode:<current> | Task:<desc> | Match:Y/N | Confidence:X%`
> Match=N or Confidence<80% → pause, suggest mode switch to user. No mode → evaluate if one is needed.

<!-- ============================================================ -->
<!-- INSTALL v2.0 — Research-backed stability rewrite              -->
<!-- Sources: DeCRIM (EMNLP 2024), ARQs (2025), Anthropic Context  -->
<!-- Engineering (2025), OpenAI GPT-4.1 Guide, Control Illusion    -->
<!-- (2025). See ~/.claude/knowledge/ for full research.           -->
<!-- ============================================================ -->

# INSTALL MODE — Context Reload Protocol v2.0

## ENFORCEMENT (read this FIRST and LAST)

You MUST complete ALL phases (P0→P5) before responding to any user request.
Do NOT skip phases. After each phase, output the verification gate. Missing gate = NOT DONE.

---

## STEP 1: Run the deterministic context loader

```bash
# This replaces manual file reading. Python reads files DETERMINISTICALLY.
# Choose the right mode:
python3 ~/Desktop/install.py full     # normal /install (distilled memory)
python3 ~/Desktop/install.py deep     # after compaction (full memory)
python3 ~/Desktop/install.py quick    # quick /install (P2 only)
python3 ~/Desktop/install.py status   # just working.md
```

Run the script FIRST. Read its output. It handles P1 (laws), P2 (context), P3 (tools), P4 (skills).
You only need to do P0 (PURGE) and P5 (REALIGN) manually.

WHY: AI file-reading is probabilistic (63.8% compliance per research). Python is deterministic.
Same files, same order, every time. No variance between sessions.

---

## How It Works (one paragraph)

LLMs weight recent tokens > distant tokens (U-shaped attention). /install floods the context tail with fresh reads from source-of-truth files, outweighing stale beliefs via recency. It does NOT erase context — it deprioritizes it. For critical corruption (3+ failed approaches), recommend user start a NEW SESSION (the only true purge).

---

## P0: PURGE [HARD — cannot skip]

WHY: Label old beliefs as SUSPECT so fresh reads override them.

**Do these 4 things:**
1. Assess corruption risk: `low | medium | high | critical`
2. List degradation symptoms (what went wrong)
3. Label all unverified facts from earlier turns → SUSPECT
4. Label all numeric values/coordinates from earlier → INVALIDATED

**Output this exact block:**
```
INSTALL MODE ACTIVATED
Corruption risk: [level]
Symptoms: [list]
DEPRIORITIZING: All prior assumptions labeled SUSPECT.
```

<gate_P0>
✓ Corruption level assessed
✓ Symptoms listed
✓ SUSPECT labels applied
→ Proceed to P1
</gate_P0>

---

## P1: IRON LAWS [SOFT]

WHY: Governance rules may have drifted during long conversation. Re-read from files, not memory.

**Do these 2 things:**
1. `~/.claude/CLAUDE.md` — re-read if behavior drifted (auto-loaded at session start, so only re-read if needed)
2. `~/Desktop/CLAUDE.md` — ALWAYS read (project-specific, not auto-loaded)

**Output this exact block:**
```
P1 IRON LAWS: LOADED
Key constraints:
  1. [most relevant to current task]
  2. [second]
  3. [third]
```

<gate_P1>
✓ ~/.claude/CLAUDE.md checked
✓ ~/Desktop/CLAUDE.md read
✓ Top 3 constraints identified
→ Proceed to P2
</gate_P1>

---

## P2: CONTEXT [HARD]

WHY: Without reading memory files, the AI will guess what it was doing — violating anti-hallucination principle 2.

**Step A — Scan conversation** (last ~10 turns):
Extract: current task (1 sentence) | status | failure log | user feedback

**Step B — Load memory files** (strict order):

```
ALWAYS load (parallel reads OK):
  1. ~/Desktop/memory/working.md              ← current task state
  2. ~/Desktop/memory/episodes.distilled.md   ← timeline index
  3. ~/Desktop/memory/facts.distilled.md      ← env/tools/prefs
  4. ~/Desktop/memory/strategies.distilled.md  ← methods/anti-patterns

ALSO load if auto-compacted OR distilled insufficient:
  5. ~/Desktop/memory/episodes.md             ← full timeline
  6. ~/Desktop/memory/facts.md                ← full facts
  7. ~/Desktop/memory/strategies.md           ← full strategies

FALLBACK if 4-file system incomplete:
  8. ~/Desktop/memorydistillation.md          ← legacy compressed
  9. ~/Desktop/memory.md                      ← legacy full
```

**Mid-session search strategy:**
```
Current task state?     → working.md
What happened when?     → episodes.md (.distilled for index)
Tool capability/config? → facts.md (.distilled for quick lookup)
How-to / proven method? → strategies.md (.distilled for quick lookup)
Semantic knowledge?     → ~/.claude/knowledge/*.distilled.md
Full verification?      → read the non-distilled version
Keyword search?         → Grep pattern="keyword" path="~/Desktop/memory/"
```

**Output this exact block:**
```
P2 CONTEXT: RESTORED
Task: [one sentence]
Status: [done/in-progress/blocked]
Done: [list]
Failed: [list — DO NOT RETRY these]
User said: [key quotes]
Next: [what to do]
```

<gate_P2>
✓ Conversation scanned
✓ working.md loaded
✓ At least 3 distilled files loaded
✓ Task identified in one sentence
→ Proceed to P3
</gate_P2>

---

## P3: TOOLS [HARD]

WHY: Without tool inventory, the AI will hallucinate capabilities or miss available tools.

**Do these 2 things:**
1. Read `~/Desktop/memory/facts.distilled.md` (pre-inventoried tools + known limitations)
2. Run `Glob ~/Desktop/*.py` (verify against facts, catch new files)

If new .py files found not in facts → read their headers, note for facts.md update.

**Output this exact block:**
```
P3 TOOLS: INVENTORIED
Source: facts.distilled.md + Glob
[tool list with capabilities and KNOWN LIMITATIONS]
Total: [N] tools
Relevant to current task: [list]
```

<gate_P3>
✓ facts.distilled.md read
✓ Glob executed
✓ Tool count matches reality
→ Proceed to P4
</gate_P3>

---

## P4: SKILLS [SOFT]

WHY: Ensures the right analysis/action modes are activated for the current task.

**Do these 2 things:**
1. Cross-reference current task (from P2) with: `ls ~/.claude/commands/*.md`
2. Check `~/.claude/knowledge/*.distilled.md` for relevant domain knowledge

**Output this exact block:**
```
P4 SKILLS: LOADED
Relevant skills: [list with one-line reason]
Relevant knowledge: [list distilled files]
Recommended mode: [skill name]
```

<gate_P4>
✓ Skills directory scanned
✓ Knowledge directory checked
✓ Recommended mode identified
→ Proceed to P5
</gate_P4>

---

## P5: REALIGN [HARD]

WHY: Forces explicit planning before action. Without this, the AI starts doing before thinking.

**Do these 3 things:**
1. Synthesize P0-P4 into an action plan
2. Record timestamp via `date +%H:%M`
3. Update `~/Desktop/memory/working.md` with current task + timestamp

**Output this exact block:**
```
INSTALL COMPLETE
==========================================
Task: [one sentence]
Strategy: [planned approach — NOT trial-and-error]
Tools: [which tools, how they'll be used]
Skills: [active modes]
First action: [specific next step]
Timestamp: [HH:MM from date command]
==========================================
```

<gate_P5>
✓ Action plan stated
✓ Timestamp recorded
✓ working.md updated
✓ ALL 6 gates passed
→ INSTALL COMPLETE — may now respond to user
</gate_P5>

---

## Automatic Triggers (3 Layers)

Any ONE layer can fire /install independently:

### Layer 1: Auto-Compaction [MANDATORY — no choice]

If the session shows a system summary message ("This session is being continued from a previous conversation") → compaction occurred → /install is MANDATORY.

Compaction rules:
- P2 Step B: MUST load full memory files (not just distilled)
- Corruption risk: HIGH minimum
- All pre-compaction values: INVALIDATED

### Layer 2: Time-Based [enforceable]

Every /install records a timestamp in P5. To check: run `date +%H:%M`.
- ≥10 minutes since last /install → trigger /install
- No /install done yet → session start = time zero

### Layer 3: Symptom-Based [continuous]

```
Repeating a failed approach?           → /install
Guessing instead of measuring?         → /install
Acting before planning?                → /install
User expressed frustration/correction? → /install
Confident about unverified thing?      → /install
Using old values without re-verifying? → /install
```

### Combined Rules

```
Auto-compaction detected           → MANDATORY /install
2+ symptoms                        → suggest /install to user
1 symptom + ≥10 min               → suggest /install to user
≥10 min + no symptoms             → be vigilant, check date
```

---

## Iron Laws (INSTALL-specific)

1. **[HARD] PURGE is honest** — deprioritizes via recency, does NOT erase. Critical corruption → recommend new session.
2. **[HARD] Read, don't recall** — files must be READ, not remembered from conversation.
3. **[HARD] Failed = failed** — never retry same approach without fundamentally different strategy.
4. **[HARD] Plan before act** — after INSTALL, first action is planning, not execution.
5. **[HARD] Order is sacred** — P0→P1→P2→P3→P4→P5. Never reorder.
6. **[HARD] Gates are mandatory** — a phase without its verification gate output = phase NOT DONE.
7. **[SOFT] Minimal loading** — load only what current task needs.
8. **[PREF] English output** — all INSTALL output in English.

---

## Quick Reference

```
/install              → Full P0-P5 reload
/install quick        → P0 + P1 + P2 only (purge + laws + context)
/install memory       → P0 + P2 with forced full memory read
/install tools        → P0 + P3 only (purge + tools inventory)
```

---

## Knowledge Deposit

After INSTALL, if session produced significant insights:
1. Ask user: "Save insights to knowledge base?"
2. Write full version → `~/.claude/knowledge/YYYY-MM-DD-<keyword>.md`
3. Five-layer distillation → `~/.claude/knowledge/YYYY-MM-DD-<keyword>.distilled.md` (target ≤25%)

---

## ENFORCEMENT (repeated — read this LAST)

You MUST complete ALL phases (P0→P1→P2→P3→P4→P5) before responding to any user request.
You MUST output every verification gate. Missing gate = phase not done = INSTALL incomplete.
Do NOT skip phases. Do NOT abbreviate gates. Do NOT start working before P5 gate passes.

---

Now begin INSTALL:
