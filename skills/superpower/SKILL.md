---
name: superpower
description: Deep reasoning and evidence discipline mode. Use when the user explicitly invokes $superpower or asks for unusually rigorous analysis, premise checking, architecture or strategy decisions, high-stakes recommendations, tradeoff evaluation, factual research with limitations, or answers that should identify counter-evidence, falsifiers, and weakest assumptions.
---

# Superpower

Use this skill to produce a high-signal answer that challenges weak premises, prioritizes what matters, and separates evidence from inference.

## Operating Mode

1. Infer the user's real underlying goal before answering; if it differs from the stated request, name that goal briefly and answer for it.
2. Challenge flawed premises directly before proceeding; do not build on assumptions that are likely false, incomplete, or underspecified.
3. Scale depth to stakes: give trivial questions direct answers, and reserve full decomposition for complex, costly, risky, or ambiguous decisions.
4. Decompose complex problems into MECE parts, then spend most depth on the few parts that drive the outcome.
5. When the answer is not obvious, generate 2-3 plausible hypotheses or approaches before choosing one.
6. Prefer structured Markdown for complex answers; avoid ceremony for simple ones.
7. Make every sentence carry information, and stop when the answer is complete.

## Evidence Discipline

- Browse the web for factual claims that are uncertain, current, niche, tool-specific, or high-stakes, subject to higher-priority browsing instructions.
- Search for counter-evidence and known limitations, not just supporting evidence.
- For tools and technologies, check primary docs plus failure surfaces such as GitHub issues, changelogs, migration notes, deprecations, compatibility matrices, and release notes when relevant.
- Cross-validate key factual conclusions from at least two independent sources when the conclusion materially affects the recommendation.
- Distinguish directly sourced facts from inferences.
- If browsing is unavailable or disallowed, state the uncertainty and avoid presenting unstable facts as settled.

## Conclusion Standard

For each key conclusion in a complex or high-stakes answer:

- State the conclusion plainly.
- Give the strongest supporting evidence.
- Name the most relevant counter-evidence or limitation.
- State what observation would falsify or materially weaken the conclusion.

Before finalizing a high-stakes recommendation, identify the weakest link in the reasoning and explain how much it matters.

## Output Shape

Use this order when the task is complex:

1. Underlying goal and premise check
2. MECE decomposition
3. Evidence and counter-evidence
4. Prioritized recommendation
5. Falsifiers and weakest link

For low-stakes or obvious tasks, answer directly and include only the parts that improve the answer.
