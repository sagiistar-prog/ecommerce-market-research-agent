# E-commerce Market Research Agent

An AI market research agent for cross-border ecommerce and content growth teams. It turns a product brief, target country, price band, and channel plan into a structured market report with competitor positioning, buyer personas, content angles, messaging claims, and risk prompts.

This repository is designed as an independent GitHub portfolio project. The demo is intentionally safe: it uses fictional categories and anonymized sample data only, and it does not scrape or fetch live market data.

## Product Value

Cross-border ecommerce teams often need to answer the same questions before testing a new product:

- Which buyer segments are likely to care first?
- How should the product be positioned against nearby alternatives?
- What claims need stronger evidence before being used in ads or listings?
- Which content hooks can be tested without overpromising?
- What risks should a human operator review before launch?

The agent standardizes that work into a repeatable workflow. It helps operators move from a vague product idea to a report that is useful for merchandising, creator briefs, landing pages, listing copy, and paid content tests.

## Content Growth Value

The agent is not only a research summarizer. It converts research inputs into growth-ready assets:

- Short-form content hooks by channel intent.
- Benefit-led messaging pillars.
- Persona-specific objection handling.
- Competitor matrix for creator and listing differentiation.
- Human review prompts for claims, compliance, sourcing, and evidence gaps.

This makes it useful for teams that need a fast research-to-content loop while still keeping evidence quality visible.

## Safe Demo

Run the demo from the project root:

```bash
python scripts/generate_market_report.py --input examples/sample_product_brief.md --competitors examples/sample_competitor_table.csv --output examples/generated_market_report.md --rules configs/research_rules.yaml --dry-run
```

The command only reads local files under `examples/` and `configs/`. It does not perform network requests.

## What The Agent Produces

- Market context summary.
- Competitor matrix.
- Price-band interpretation.
- Buyer personas.
- Content angles and hooks.
- Messaging pillars.
- Risk register.
- Evidence notes and human review checklist.

## Governance Built In

The repository includes configuration files that make research quality explicit:

- `configs/source_policy.yaml` defines data source priority and forbidden sources.
- `configs/research_rules.yaml` defines evidence levels, safe-demo boundaries, and human review prompts.
- `scripts/portfolio_audit.ps1` checks project structure, secret-like strings, demo constraints, and network-free implementation.

Evidence levels are surfaced in the generated report so users can distinguish demo fixtures, user-provided material, curated exports, public references, and low-confidence assumptions.

## Repository Structure

```text
README.md
AGENTS.md
.gitignore
requirements.txt
LICENSE
docs/case-study.md
docs/workflow.md
docs/research-framework.md
docs/safe-demo.md
skills/ecommerce-market-research-agent/SKILL.md
scripts/generate_market_report.py
scripts/portfolio_audit.ps1
configs/research_rules.yaml
configs/source_policy.yaml
examples/sample_product_brief.md
examples/sample_competitor_table.csv
examples/generated_market_report.md
```

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

`PyYAML` is listed for normal YAML parsing. The demo configuration is JSON-compatible YAML, so the generator can also run with the Python standard library if `PyYAML` is not installed.

## Portfolio Audit

```powershell
powershell -ExecutionPolicy Bypass -File scripts/portfolio_audit.ps1
```

The audit checks for required files, secret-like strings, safe-demo wording, and accidental networking imports.

## Safety Notes

- No credentials, secret keys, real customer data, or real company profile is included.
- Example competitors are fictional.
- Example metrics are synthetic and should not be treated as market facts.
- This public portfolio repository is intentionally generalized and does not include private business logic, client data, internal product strategy, or confidential information from any real project.
- The generated report is a portfolio demo, not investment, legal, compliance, or sourcing advice.
