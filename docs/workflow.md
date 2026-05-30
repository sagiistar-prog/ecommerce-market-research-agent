# Workflow

## 1. Input Product Brief

The user provides:

- Product category.
- Target country.
- Price band.
- Primary channels.
- Audience hypothesis.
- Research goal.
- Constraints.

The Safe Demo uses `examples/sample_product_brief.md`.

Users can also edit this input through the local web app.

## 2. Load Competitor Fixture

The agent reads a local CSV with fictional competitor entries:

- Brand name.
- Price.
- Channel.
- Positioning claim.
- Content hook.
- Evidence level.

The Safe Demo uses `examples/sample_competitor_table.csv`.

The local web app accepts the same CSV shape in the browser.

## 3. Apply Research Rules And Preferences

The generator loads local configs to apply:

- Source priority.
- Evidence levels.
- Human review prompts.
- Safe-demo boundaries.
- Report preferences for product manager and content growth review.

## 4. Generate Research Report

The report includes:

- Executive snapshot.
- Market hypotheses.
- Competitor matrix.
- Persona map.
- Content growth angles.
- Messaging pillars.
- Risk register.
- Human review checklist.

The report separates facts, inferences, and recommendations so readers can see what came from fixtures and what is a hypothesis.

## 5. Human Review

Before using any output in real ecommerce operations, a human should review:

- Product claims.
- Compliance-sensitive wording.
- Country-specific restrictions.
- Supplier proof.
- Pricing and shipping assumptions.
- Any content claim that implies performance, safety, health, origin, certification, or durability.

## 6. Portfolio Audit

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/portfolio_audit.ps1
```

The audit checks that the repository remains safe to publish.

## 7. Local Web App

Run:

```powershell
py -3 scripts/app_server.py --port 8765
```

The app serves a local browser interface for loading sample inputs, editing demo data, generating reports, copying Markdown, and downloading the result.
