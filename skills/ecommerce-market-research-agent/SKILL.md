# E-commerce Market Research Agent Skill

Use this skill when a user wants to generate or improve a cross-border ecommerce market research report from a product brief, target country, price band, channel plan, and competitor notes.

## Safety Boundary

- Use fictional or anonymized examples unless the user explicitly provides approved data.
- Do not fetch live ecommerce data in the Safe Demo.
- Do not include tokens, customer data, private chats, or real company profiles.
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
python scripts/generate_market_report.py --input examples/sample_product_brief.md --competitors examples/sample_competitor_table.csv --output examples/generated_market_report.md --rules configs/research_rules.yaml --dry-run
```

