# Safe Demo

The Safe Demo proves the workflow without touching real market data.

## Demo Command

```bash
python scripts/generate_market_report.py --input examples/sample_product_brief.md --competitors examples/sample_competitor_table.csv --output examples/generated_market_report.md --rules configs/research_rules.yaml --dry-run
```

## What It Uses

- `examples/sample_product_brief.md`
- `examples/sample_competitor_table.csv`
- `configs/research_rules.yaml`

All example product and competitor data is fictional.

## What It Does Not Do

- Does not scrape websites.
- Does not call APIs.
- Does not read private accounts.
- Does not use real customer data.
- Does not include real company research.
- Does not produce verified market-size estimates.

## Expected Output

The output report is written to:

```text
examples/generated_market_report.md
```

The report includes market hypotheses, competitor matrix, buyer personas, content hooks, risks, and a human review checklist.

## How To Interpret Results

Treat all recommendations as a structured demonstration of the agent workflow. In a production setting, each claim should be linked to reviewed evidence before it is used in product listings, ads, creator briefs, or sourcing decisions.

