# Safe Demo

The Safe Demo proves the workflow without touching real market data.

## Demo Command

```bash
python scripts/generate_market_report.py --input examples/sample_product_brief.md --competitors examples/sample_competitor_table.csv --output examples/generated_market_report.md --rules configs/research_rules.yaml --sources configs/source_policy.yaml --preferences configs/user_preferences.yaml --dry-run
```

Windows launcher alternative:

```powershell
py -3 scripts/generate_market_report.py --input examples/sample_product_brief.md --competitors examples/sample_competitor_table.csv --output examples/generated_market_report.md --rules configs/research_rules.yaml --sources configs/source_policy.yaml --preferences configs/user_preferences.yaml --dry-run
```

## What It Uses

- `examples/sample_product_brief.md`
- `examples/sample_competitor_table.csv`
- `configs/research_rules.yaml`
- `configs/source_policy.yaml`
- `configs/user_preferences.yaml`

All example product and competitor data is fictional.

## What It Does Not Do

- Does not scrape websites.
- Does not call APIs.
- Does not read private accounts.
- Does not use real customer data.
- Does not include real company research.
- Does not produce verified market-size estimates.

## Browser UI

Run:

```powershell
py -3 scripts/app_server.py --port 8765
```

Open `http://127.0.0.1:8765` to use the local app. The UI uses the same fictional examples and local configs as the command-line demo.

## Expected Output

The output report is written to:

```text
examples/generated_market_report.md
```

The report includes executive summary, target market hypothesis, user segments, competitor matrix summary, price band observation, product positioning, content growth angles, channel strategy, risk notes, and evidence-level review notes.

## How To Interpret Results

Treat all recommendations as a structured demonstration of the agent workflow. In a production setting, each claim should be linked to reviewed evidence before it is used in product listings, ads, creator briefs, or sourcing decisions.
