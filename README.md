# E-commerce Market Research Agent

## Interviewer 30-Second Version

This is a Safe Demo of an AI market research agent for cross-border ecommerce and content growth. It turns a fictional product brief, fictional competitor table, evidence rules, source policy, and user preferences into a structured market research report.

The project demonstrates AI product manager judgment: facts, inferences, and recommendations are separated; every output is tied to evidence levels; risky claims trigger manual review; and the demo contains no real commercial data.

## What It Shows

- Market research Agent workflow for early ecommerce category testing.
- Content growth translation from research notes into channel angles and messaging pillars.
- Evidence grading so demo facts, hypotheses, and recommendations are not mixed together.
- Manual review gates for product claims, compliance assumptions, pricing, shipping, and public copy.
- A Safe Demo that only reads local `examples/` and `configs/` files.
- A portfolio audit that checks structure, secrets, local paths, demo safety, and business confidentiality.

This public portfolio repository is intentionally generalized and does not include private business logic, client data, internal product strategy, or confidential information from any real project.

## Product Value

Cross-border ecommerce teams often need a fast but disciplined way to answer:

- Which buyer segments should we test first?
- Which competitor positions are crowded?
- What price-band assumptions need validation?
- Which content hooks can be tested without overclaiming?
- What must a human review before public use?

The agent standardizes that work into a repeatable workflow. It helps move from a rough product idea to an evidence-aware report that can support merchandising, creator briefs, landing pages, listing copy, and content tests.

## Content Growth Value

The output is not only a research summary. It turns research inputs into growth-ready assets:

- Short-form content hooks by channel intent.
- Benefit-led messaging pillars.
- Persona-specific objections and responses.
- Competitor matrix for positioning decisions.
- Risk notes and manual review prompts for claims and evidence gaps.

## Safe Demo

Run the demo from the project root:

```bash
python scripts/generate_market_report.py --input examples/sample_product_brief.md --competitors examples/sample_competitor_table.csv --output examples/generated_market_report.md --rules configs/research_rules.yaml --sources configs/source_policy.yaml --preferences configs/user_preferences.yaml --dry-run
```

Windows launcher alternative:

```powershell
py -3 scripts/generate_market_report.py --input examples/sample_product_brief.md --competitors examples/sample_competitor_table.csv --output examples/generated_market_report.md --rules configs/research_rules.yaml --sources configs/source_policy.yaml --preferences configs/user_preferences.yaml --dry-run
```

The command only reads local files under `examples/` and `configs/`. It does not scrape, fetch, or verify live market data.

## What The Agent Produces

- Executive summary.
- Target market hypothesis.
- User segments.
- Competitor matrix summary.
- Price band observation.
- Product positioning.
- Content growth angles.
- Channel strategy.
- Risk notes.
- Evidence level and manual review notes.

## Governance Built In

The repository includes configuration files and an audit script that make research quality and public-safety boundaries explicit:

- `configs/research_rules.yaml` defines evidence levels, safe-demo boundaries, and manual review prompts.
- `configs/source_policy.yaml` defines source priority without relying on private source bundles.
- `configs/user_preferences.yaml` tunes the report for product manager and content growth review.
- `scripts/portfolio_audit.ps1` checks required files, secret-like strings, local paths, safe-demo constraints, network-free implementation, and business confidentiality terms.

Evidence levels are surfaced in the generated report so readers can distinguish demo fixtures, reviewed inputs, public references, corroborated evidence, and low-confidence hypotheses.

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
docs/source-policy.md
docs/interview-summary.md
docs/safe-demo.md
skills/ecommerce-market-research-agent/SKILL.md
scripts/generate_market_report.py
scripts/portfolio_audit.ps1
configs/research_rules.yaml
configs/source_policy.yaml
configs/user_preferences.yaml
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

The audit is the pre-commit gate for this public portfolio project. If it fails, do not commit or push.

## Safety Notes

- No credentials, secret keys, real customer data, or real company profile is included.
- Example competitors are fictional.
- Example metrics are synthetic and should not be treated as market facts.
- The generated report is a portfolio demo, not investment, legal, compliance, or sourcing advice.
