---
name: ecommerce-market-research-agent
description: Organize a product brief and competitor evidence into testable ecommerce research hypotheses. Use for evidence review and research planning.
---

# E-commerce Market Research Agent Skill

Use this skill when a user wants to generate or improve a cross-border ecommerce market research report from a product brief, target country, price band, channel plan, and competitor notes.

## Safety Boundary

- Use fictional or anonymized examples unless the user explicitly provides approved data.
- Do not fetch live ecommerce data in the Safe Demo.
- Do not include credentials, customer data, private chats, or real company profiles.
- Label assumptions and evidence levels.
- Add human review prompts for claims that touch compliance, sourcing, safety, health, certifications, durability, shipping, pricing, or advertising.

## Inputs

- Product brief markdown.
- Competitor table CSV.
- Research rules config.
- Optional source policy config.

## Workflow

1. Read the product brief and identify category, target country, price band, channels, audience, and constraints.
2. Read the competitor table and normalize price, channel, positioning, and content hooks.
3. Apply source priority and evidence levels from config.
4. Generate market hypotheses, not absolute market facts.
5. Create buyer personas and content growth angles.
6. Add a risk register and human review checklist.
7. Save a markdown report.

## Output Sections

- Executive snapshot.
- Research boundaries.
- Market hypotheses.
- Competitor matrix.
- Price-band read.
- Buyer personas.
- Content growth angles.
- Messaging pillars.
- Risk register.
- Human review checklist.

## Safe Demo Command

```bash
python scripts/generate_market_report.py --input examples/sample_product_brief.md --competitors examples/sample_competitor_table.csv --output examples/generated_market_report.md --rules configs/research_rules.yaml --sources configs/source_policy.yaml --preferences configs/user_preferences.yaml --dry-run
```

## Versioned plugin interface

Use the repository root as the working directory. For an installed plugin, resolve the root as two directories above this SKILL.md; never assume the user's project contains the bundled scripts.

1. Read `schemas/input.schema.json` before constructing input. Use `examples/plugin-input.json` for an offline demonstration.
2. Install `requirements-plugin.txt` into the user's chosen Python environment when needed.
3. Run `python scripts/plugin_run.py --input examples/plugin-input.json` from the plugin root. For user text, pass a JSON object through stdin; do not interpolate it into a shell command.
4. Parse stdout as one JSON object; exit 0 means success, exit 2 means an input/output/dependency error. Show the error and preserve the input rather than retrying indefinitely.
5. Present the Markdown result and material warnings. When the user asks to save artifacts, add `--output-dir output/<new-run-name>`. This creates files; an existing directory is never overwritten.

The plugin does not grant permission to read unrelated files, publish content, run rendering or access accounts. The original CLI remains available. See `docs/plugin.md` for the capability boundary and the structured error contract.
