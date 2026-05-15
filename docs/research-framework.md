# Research Framework

This framework describes the product management logic behind the E-commerce Market Research Agent. The goal is to make early market judgment repeatable without pretending that a Safe Demo has real market proof.

## Product Manager Lens

The agent treats market research as a decision artifact, not a raw summary. Each report should help a team decide:

1. Which audience segment should be tested first?
2. Which positioning lane is plausible but not yet proven?
3. Which content angles are safe enough to test?
4. Which claims require manual review before public use?
5. Which assumptions should become the next experiment?

## Input Model

The demo uses three input layers:

| Layer | Purpose | Safe Demo Source |
| --- | --- | --- |
| Product brief | Category, market, price band, channels, audience hypothesis | Fictional markdown brief |
| Competitor table | Nearby positioning examples and content hooks | Synthetic CSV fixture |
| Governance configs | Evidence levels, source priority, review prompts | Local YAML configs |

## Decision Stack

The report separates three kinds of output:

| Output Type | Meaning | Example Use |
| --- | --- | --- |
| Fact | Directly present in the local demo fixture | Brief category, target market, price band |
| Inference | Reasoned interpretation from fixture patterns | Visual transformation may be stronger than feature-led copy |
| Recommendation | Suggested next action | Test two content hooks and review claims before public use |

This separation is the main product principle. It keeps the agent useful for strategy work while preventing unsupported certainty.

## Evidence Levels

| Level | Meaning | Usage |
| --- | --- | --- |
| E0 | Fictional demo fixture | Safe Demo only |
| E1 | User-provided reviewed source | Draft analysis with owner approval |
| E2 | Reviewed public source | Low-risk observations with citation logs |
| E3 | Corroborated multi-source evidence | Recommendations with caveats |
| E4 | Unverified hypothesis | Testing backlog only |

## Content Growth Translation

The agent turns research into growth inputs:

- Persona-specific content hooks.
- Listing and landing page message pillars.
- Creator brief prompts.
- Objection handling.
- Channel test metrics.

Every content idea should include the review condition that must be satisfied before public use.

## Manual Review Gates

Manual review is required when output touches:

- Public advertising claims.
- Compliance-sensitive product language.
- Country-specific assumptions.
- Health, safety, performance, origin, warranty, or durability claims.
- Pricing, shipping, returns, and fulfillment expectations.

## What Good Output Looks Like

A strong report should be clear enough for an interviewer to see:

- The agent is productized, not just scripted.
- Evidence quality is visible.
- Safe Demo data is clearly fictional.
- Product strategy and content strategy are connected.
- Manual review is part of the workflow, not an afterthought.

