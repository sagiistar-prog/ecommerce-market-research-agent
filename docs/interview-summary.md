# Interview Summary

## One-Liner

E-commerce Market Research Agent is a Safe Demo AI product workflow that turns a fictional product brief and synthetic competitor table into an evidence-aware market research report for cross-border ecommerce and content growth.

## Why It Matters

Early ecommerce research often mixes facts, assumptions, and content ideas. This project shows how an AI product manager can structure that work into a repeatable report with evidence levels, risk notes, and manual review gates.

## What To Notice

- The demo is local-only and does not fetch live data.
- The examples are fictional and synthetic.
- The generated report separates facts, inferences, and recommendations.
- Evidence levels are visible in the output.
- Manual review is built into the workflow.
- A local browser UI makes the agent usable as a small demo app.
- The audit script acts as a pre-commit safety gate for public portfolio use.

## Product Thinking Demonstrated

- Defines an input schema around product brief, competitor fixture, source policy, and preferences.
- Adds a simple browser interface for editing inputs and generating reports.
- Converts research into audience segments, positioning, content growth angles, and channel strategy.
- Keeps risk management visible through evidence levels and review prompts.
- Designs for interview readability rather than raw automation alone.

## Safe Demo Command

```bash
python scripts/generate_market_report.py --input examples/sample_product_brief.md --competitors examples/sample_competitor_table.csv --output examples/generated_market_report.md --rules configs/research_rules.yaml --sources configs/source_policy.yaml --preferences configs/user_preferences.yaml --dry-run
```

## Public Safety Position

This repository is intentionally generalized. It does not include real customer data, real company data, confidential product plans, private operating paths, or real commercial records.
