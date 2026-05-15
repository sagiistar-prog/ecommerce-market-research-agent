# Agent Instructions

This repository is an independent portfolio project for the E-commerce Market Research Agent.

## Safety Rules

- Do not add credentials, API keys, customer records, private chat logs, or real company research data.
- Do not scrape, crawl, or fetch live ecommerce data in the Safe Demo.
- Keep examples fictional, synthetic, or clearly anonymized.
- Treat `examples/` as demo fixtures, not real market evidence.
- If new data is added, label the evidence level and add a human review prompt when claims affect compliance, sourcing, health, safety, pricing, or advertising.

## Public Portfolio Confidentiality Rules

- Public portfolio repositories must not include confidential project names, real business loops, real business models, real client information, real partners, real internal paths, real monetization design, or real product planning.
- After any optimization, run `powershell -ExecutionPolicy Bypass -File scripts\portfolio_audit.ps1`.
- If the audit fails, do not commit or push. Fix the flagged files first, then run the audit again.

## Implementation Rules

- Keep the generator local-file-only unless the README and configs are updated to describe a reviewed data policy.
- Do not add networking libraries such as `requests`, `httpx`, scraping frameworks, browser automation, or marketplace-specific SDKs for the Safe Demo.
- Prefer transparent markdown output over hidden model calls.
- Preserve `scripts/portfolio_audit.ps1` as a quick portfolio safety check.

## Demo Command

```bash
python scripts/generate_market_report.py --input examples/sample_product_brief.md --competitors examples/sample_competitor_table.csv --output examples/generated_market_report.md --rules configs/research_rules.yaml --dry-run
```

## Review Checklist

- Required files are present.
- Generated examples remain fictional.
- Configs show source priority, evidence levels, and human review prompts.
- No secrets or private data are committed.
- Safe Demo runs without network access.
- The business confidentiality audit passes before commit and push.
