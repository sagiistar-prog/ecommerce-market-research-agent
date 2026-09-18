---
name: ecommerce-market-research-agent
description: Analyze a local product brief and competitor observations, then develop product-specific hypotheses with exact evidence citations and validation plans. Use for early ecommerce product research, not autonomous live scraping or market-size forecasting.
---

# Market Research Desk

The local engine calculates sample statistics and evidence gaps. You, the host assistant, interpret the user's category, audience, constraints and decision. Python does not call a model or fetch websites.

Resolve the plugin root two directories above this SKILL.md. Run bundled scripts from that root, not the user's project. Use task-provided materials only; keep private inputs and results out of tracked examples. The Safe Demo is fictional and network-free. External research, if requested, is a separate authorized step using available tools and `docs/source-policy.md`.

## Analyze the material

Read `schemas/input.schema.json` and `docs/plugin.md` for CSV semantics. Preserve free text. Ask only for decision-critical gaps; do not invent an audience, feature, price or market. Do not convert missing prices to zero or group unlike offers to obtain statistics.

The deterministic parser recognizes labeled lines, not arbitrary prose. For a natural-language brief, use your language understanding to add `Category:`, `Target market:`, `Audience hypothesis:` and `Research goal:` lines **only from explicitly supplied information**, retaining the user's original wording below them. Chinese equivalents are 品类、目标市场、目标用户、研究问题. Leave genuinely absent values blank. Do not ask the user again for facts already present in the prose.

Use the chosen Python environment with `requirements-plugin.txt` installed. This command is a fictional demonstration, not a substitute for the user's input:

```bash
python scripts/plugin_run.py --input examples/pet-bowl-input.json --output-dir output/new-review
```

For an actual task, prepare the JSON from the user's materials or send it through stdin; do not interpolate user text into shell commands. Existing output directories are never overwritten. Exit 0 returns one JSON object; exit 2 returns a structured error. Preserve input and explain how to correct the error rather than retrying unchanged input.

Inspect `result.analysis`: supplied brief, evidence ledger, grouped statistics, observations and research tasks. URLs, dates and evidence labels are metadata, not verification. Feature matching is literal, not semantic clustering. Sample counts do not establish demand, uniqueness or market share. Synthetic and provided prices are separated even when group labels match.

Select research tasks relevant to the user's decision. Optional price-comparison gaps should not block a usability or positioning exercise. For an explicitly fictional offline exercise, explain the source limitation without demanding live collection; propose later verification only if needed for real-world use.

## Make the product judgment

Answer the actual decision question. Connect the user's task and current alternative to a specific proposed change; explain why it deserves a test and what would disprove it. Distinguish competitor claims from inferences about user needs. If the material is insufficient, recommend the smallest useful research step rather than inventing a launch recommendation.

For product or messaging hypotheses, create `decisions.json` using `schemas/decisions.schema.json`:

- Copy the exact `analysis_id` from the generated snapshot.
- Cite E001-style IDs and an exact substring from an allowed field, or `BRIEF` with `original_brief`. Do not quote a summary as source text.
- State target user, problem, proposed change, reasoning and untested assumptions. Choose the number of proposals useful to the task; do not fill a quota.
- Specify validation method, primary metric, guardrail and decision rule. Unsupported thresholds must be proposed for agreement before testing, never described as measured results.
- Keep status `hypothesis`. Require domain review before public safety, health, compliance or advertising claims.

Check references against the saved analysis:

```bash
python scripts/validate_decisions.py --analysis output/new-review/result.json --decisions output/new-review/decisions.json
```

The validator rejects stale snapshots, nonexistent IDs and quotes absent from cited fields. It proves reference integrity only; assess relevance, representativeness, contradictory evidence and reasoning yourself. `examples/pet-bowl-decisions.json` illustrates the format, not a stock answer for another category.

Present the decision, evidence, assumptions and next test concisely in the user's language. Link saved artifacts when requested. Do not claim live research, measured customer value or automatic model evaluation from local checks.

## Hand the hypotheses to the reviewer

After validating `decisions.json`, explain how to import it in the local app's Hypotheses view after analyzing the matching brief and CSV. The user records Plan a test, Defer or Reject with a reason; leave proposals unreviewed until they choose. Do not manufacture reviewer choices or measured outcomes.

A downloaded review JSON includes the evidence and proposal snapshots, choices and reasons. To resume, analyze the same inputs and import that review file. Changed proposals invalidate old choices. Markdown notes are for reading, not round-trip import. The app does not automatically save; ask the user to download their review before closing. `validation_status: not_measured` remains true after a completed review.
