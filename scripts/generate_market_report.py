#!/usr/bin/env python3
"""Generate a local-only ecommerce market research report from safe demo inputs."""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import date
from pathlib import Path
from statistics import mean
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - exercised only when PyYAML is absent
    yaml = None


NETWORK_IMPORTS_ARE_INTENTIONALLY_ABSENT = True


def load_config(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        loaded = yaml.safe_load(text)
        return loaded if isinstance(loaded, dict) else {}
    loaded = json.loads(text)
    return loaded if isinstance(loaded, dict) else {}


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def parse_product_brief(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    fields: dict[str, str] = {"raw_text": text}

    for line in text.splitlines():
        clean = line.strip().lstrip("-").strip()
        if not clean:
            continue

        bold_match = re.match(r"\*\*(.+?)\*\*:\s*(.+)$", clean)
        plain_match = re.match(r"([A-Za-z][A-Za-z /_-]{2,40}):\s*(.+)$", clean)
        match = bold_match or plain_match
        if match:
            key = normalize_key(match.group(1))
            fields[key] = match.group(2).strip()

    fields.setdefault("category", "Unspecified fictional category")
    fields.setdefault("target_country", "Unspecified target country")
    fields.setdefault("price_band", "Unspecified price band")
    fields.setdefault("primary_channels", "Unspecified channels")
    fields.setdefault("audience_hypothesis", "Unspecified audience")
    fields.setdefault("research_goal", "Generate an early market research report")
    fields.setdefault("positioning_note", "Keep claims evidence-aware and human reviewed")
    fields.setdefault("constraints", "Use safe local demo inputs only")
    return fields


def load_competitors(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"No competitor rows found in {path}")
    return rows


def parse_price(value: str) -> float | None:
    match = re.search(r"\d+(?:\.\d+)?", value or "")
    return float(match.group(0)) if match else None


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    header_line = "| " + " | ".join(headers) + " |"
    divider = "| " + " | ".join(["---"] * len(headers)) + " |"
    row_lines = ["| " + " | ".join(cell.replace("\n", " ") for cell in row) + " |" for row in rows]
    return "\n".join([header_line, divider, *row_lines])


def config_table(config: dict[str, Any], key: str, headers: list[str], fields: list[str]) -> str:
    items = config.get(key, [])
    if not isinstance(items, list):
        return "_No config entries found._"
    rows: list[list[str]] = []
    for item in items:
        if isinstance(item, dict):
            rows.append([str(item.get(field, "")) for field in fields])
    return markdown_table(headers, rows)


def competitor_table(rows: list[dict[str, str]]) -> str:
    table_rows = []
    for row in rows:
        table_rows.append(
            [
                row.get("brand", ""),
                f"${row.get('price_usd', '')}",
                row.get("channel", ""),
                row.get("positioning_claim", ""),
                row.get("key_feature", ""),
                row.get("evidence_level", "E0"),
            ]
        )
    return markdown_table(
        ["Fictional competitor", "Price", "Channel", "Positioning", "Key feature", "Evidence"],
        table_rows,
    )


def channel_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        channel = row.get("channel", "Unspecified")
        counts[channel] = counts.get(channel, 0) + 1
    return counts


def build_content_angles(brief: dict[str, str], rows: list[dict[str, str]]) -> list[list[str]]:
    category = brief["category"]
    country = brief["target_country"]
    hooks = [
        [
            "Desk reset transformation",
            "Short-video commerce",
            f"Turn a cramped desk into a warmer {category} setup in under 30 seconds.",
            "Needs product footage and no productivity promise.",
        ],
        [
            "Small-space proof",
            "Creator storefront",
            f"Show how the kit fits a compact apartment or student desk in {country}.",
            "Needs dimension proof and setup photos.",
        ],
        [
            "Giftable upgrade",
            "Search-led listing",
            "Position as an easy desk gift for remote work, study, and creator corners.",
            "Needs packaging, shipping, and return-policy review.",
        ],
        [
            "Magnetic layout demo",
            "Short-video commerce",
            "Show three rearranged layouts from the same kit.",
            "Needs durability and attachment review.",
        ],
    ]

    for row in rows[:3]:
        hooks.append(
            [
                f"Differentiate from {row.get('brand', 'fictional competitor')}",
                row.get("channel", "Channel test"),
                f"Contrast against '{row.get('content_hook', 'generic setup content')}' with a clearer use case.",
                "Treat as synthetic competitor observation.",
            ]
        )
    return hooks


def build_report(
    brief: dict[str, str],
    competitors: list[dict[str, str]],
    rules: dict[str, Any],
    input_path: Path,
    competitor_path: Path,
    dry_run: bool,
) -> str:
    prices = [price for price in (parse_price(row.get("price_usd", "")) for row in competitors) if price is not None]
    avg_price = mean(prices) if prices else 0.0
    min_price = min(prices) if prices else 0.0
    max_price = max(prices) if prices else 0.0
    counts = channel_counts(competitors)
    channel_summary = ", ".join(f"{channel}: {count}" for channel, count in counts.items())

    source_table = config_table(
        rules,
        "source_priority",
        ["Rank", "Source", "Safe Demo Status", "Evidence"],
        ["rank", "source", "safe_demo_status", "evidence_level"],
    )
    evidence_table = config_table(
        rules,
        "evidence_levels",
        ["Level", "Label", "Confidence", "Allowed Use"],
        ["level", "label", "confidence", "allowed_use"],
    )
    review_prompts = rules.get("human_review_prompts", [])
    if not isinstance(review_prompts, list):
        review_prompts = []

    content_rows = build_content_angles(brief, competitors)

    report_lines = [
        "# Generated Market Research Report",
        "",
        f"Generated on: {date.today().isoformat()}",
        "",
        "## Safe Demo Notice",
        "",
        "This report was generated from local fictional examples only. It does not scrape, fetch, or verify live market data. Treat all recommendations as hypotheses for portfolio demonstration.",
        "",
        f"- Dry run mode: {'enabled' if dry_run else 'disabled'}",
        f"- Product brief: `{input_path.as_posix()}`",
        f"- Competitor fixture: `{competitor_path.as_posix()}`",
        "- Evidence level for demo inputs: E0",
        "",
        "## Executive Snapshot",
        "",
        markdown_table(
            ["Field", "Value"],
            [
                ["Category", brief["category"]],
                ["Target country", brief["target_country"]],
                ["Price band", brief["price_band"]],
                ["Primary channels", brief["primary_channels"]],
                ["Audience hypothesis", brief["audience_hypothesis"]],
                ["Research goal", brief["research_goal"]],
            ],
        ),
        "",
        "## Research Boundaries",
        "",
        f"- Constraints: {brief['constraints']}",
        f"- Positioning note: {brief['positioning_note']}",
        "- The report separates observed demo fixtures from generated hypotheses.",
        "- Human review is required before using any claim in public commercial content.",
        "",
        "## Source Priority",
        "",
        source_table,
        "",
        "## Evidence Levels",
        "",
        evidence_table,
        "",
        "## Market Hypotheses",
        "",
        f"- The strongest early test audience is likely inside the stated audience hypothesis: {brief['audience_hypothesis']}",
        f"- The price band of {brief['price_band']} suggests the product should be framed as an accessible upgrade rather than a premium hardware purchase.",
        f"- Channel coverage in the fictional fixture is concentrated across: {channel_summary}.",
        "- Visual transformation content is likely more useful than technical feature lists for first-touch discovery.",
        "- Search-led listing copy should emphasize concrete use cases, dimensions, setup simplicity, and giftability.",
        "",
        "## Fictional Competitor Matrix",
        "",
        competitor_table(competitors),
        "",
        "## Price-Band Read",
        "",
        f"- Fictional competitor price range: ${min_price:.0f}-${max_price:.0f}.",
        f"- Fictional average competitor price: ${avg_price:.0f}.",
        f"- Demo interpretation: the target price band should preserve a clear value story below the highest fictional competitor while still supporting giftable packaging and visual content assets.",
        "",
        "## Buyer Personas",
        "",
        markdown_table(
            ["Persona", "Job To Be Done", "Likely Objection", "Content Response"],
            [
                [
                    "Small-space remote worker",
                    "Make a compact desk feel more intentional for calls and evening work.",
                    "Worried it will add clutter.",
                    "Show cable routing, footprint, and before-after desk resets.",
                ],
                [
                    "Student creator",
                    "Create a more expressive setup for study clips and casual content.",
                    "Worried it looks complicated.",
                    "Use quick setup videos and rearranged magnetic layouts.",
                ],
                [
                    "Gift buyer",
                    "Find a useful desk gift that feels personal without needing exact specs.",
                    "Worried about compatibility and returns.",
                    "Make compatibility, package contents, and return policy clear.",
                ],
            ],
        ),
        "",
        "## Content Growth Angles",
        "",
        markdown_table(
            ["Angle", "Channel", "Hook", "Review Needed"],
            content_rows,
        ),
        "",
        "## Messaging Pillars",
        "",
        "- Compact transformation: focus on visible desk improvement in a small area.",
        "- Rearrangeable setup: show modular layouts without claiming technical superiority.",
        "- Giftable utility: position as useful, visual, and easy to understand.",
        "- Low-friction setup: emphasize simple installation only if supported by product proof.",
        "",
        "## Risk Register",
        "",
        markdown_table(
            ["Risk", "Why It Matters", "Mitigation"],
            [
                [
                    "Unsupported performance claims",
                    "Productivity, wellness, and focus claims can be misleading if unverified.",
                    "Use visual and functional claims only; require human review for stronger wording.",
                ],
                [
                    "Country-specific compliance gaps",
                    "Lighting products may need electrical, labeling, or packaging review.",
                    f"Run a {brief['target_country']} compliance check before launch.",
                ],
                [
                    "Content overpromises",
                    "Short-form hooks can exaggerate benefits.",
                    "Attach evidence labels and avoid before-after claims that imply guaranteed outcomes.",
                ],
                [
                    "Price and shipping assumptions",
                    "The report uses synthetic data, not verified landed cost.",
                    "Confirm margins, duties, fulfillment times, warranty, and returns.",
                ],
            ],
        ),
        "",
        "## Human Review Checklist",
        "",
    ]

    for prompt in review_prompts:
        report_lines.append(f"- {prompt}")

    report_lines.extend(
        [
            "",
            "## Next Experiments",
            "",
            "- Test two short-video hooks: desk reset transformation vs. magnetic layout demo.",
            "- Test one search-led listing variant focused on compact setup proof.",
            "- Create a creator brief that asks for honest setup time, footprint, and cable visibility.",
            "- Collect reviewed evidence before turning any hypothesis into a public claim.",
            "",
            "## Demo Provenance",
            "",
            "- Product and competitor names are fictional.",
            "- Metrics are synthetic and should not be treated as market facts.",
            "- No token, private customer data, real company data, or live marketplace data was used.",
        ]
    )

    return "\n".join(report_lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a local-only ecommerce market research report.")
    parser.add_argument("--input", required=True, type=Path, help="Path to product brief markdown.")
    parser.add_argument("--competitors", required=True, type=Path, help="Path to fictional competitor CSV.")
    parser.add_argument("--output", required=True, type=Path, help="Path to write generated markdown report.")
    parser.add_argument("--rules", required=True, type=Path, help="Path to research rules config.")
    parser.add_argument("--dry-run", action="store_true", help="Mark output as Safe Demo dry run.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    brief = parse_product_brief(args.input)
    competitors = load_competitors(args.competitors)
    rules = load_config(args.rules)

    report = build_report(
        brief=brief,
        competitors=competitors,
        rules=rules,
        input_path=args.input,
        competitor_path=args.competitors,
        dry_run=args.dry_run,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"Wrote market research report to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

