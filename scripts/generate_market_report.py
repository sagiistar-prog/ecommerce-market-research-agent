#!/usr/bin/env python3
"""Generate a local-only ecommerce market research report from safe demo inputs."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path
from statistics import mean
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - exercised only when PyYAML is absent
    yaml = None


NETWORK_IMPORTS_ARE_INTENTIONALLY_ABSENT = True


def load_config(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}

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

        bold_colon_inside = re.match(r"\*\*(.+?):\*\*\s*(.+)$", clean)
        bold_colon_outside = re.match(r"\*\*(.+?)\*\*:\s*(.+)$", clean)
        plain_match = re.match(r"([A-Za-z][A-Za-z /_-]{2,40}):\s*(.+)$", clean)
        match = bold_colon_inside or bold_colon_outside or plain_match
        if match:
            key = normalize_key(match.group(1))
            fields[key] = match.group(2).strip()

    defaults = {
        "category": "Fictional ecommerce product category",
        "target_country": "Fictional target market",
        "price_band": "Fictional price band",
        "primary_channels": "Short-form content and search-led marketplace listing",
        "audience_hypothesis": "Early adopters who want a practical visual upgrade.",
        "research_goal": "Generate an evidence-aware early market research report.",
        "positioning_note": "Keep claims evidence-aware and human reviewed.",
        "constraints": "Use safe local demo inputs only.",
    }
    for key, value in defaults.items():
        fields.setdefault(key, value)
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
    return markdown_table(headers, rows) if rows else "_No config entries found._"


def source_policy_table(source_policy: dict[str, Any], rules: dict[str, Any]) -> str:
    if source_policy.get("source_priority"):
        return config_table(
            source_policy,
            "source_priority",
            ["Rank", "Source type", "Evidence", "Notes"],
            ["rank", "source_type", "evidence_level", "notes"],
        )

    return config_table(
        rules,
        "source_priority",
        ["Rank", "Source", "Safe Demo Status", "Evidence"],
        ["rank", "source", "safe_demo_status", "evidence_level"],
    )


def competitor_matrix(rows: list[dict[str, str]]) -> str:
    table_rows = []
    for row in rows:
        table_rows.append(
            [
                row.get("brand", ""),
                f"${row.get('price_usd', '')}",
                row.get("channel", ""),
                row.get("positioning_claim", ""),
                row.get("key_feature", ""),
                row.get("content_hook", ""),
                row.get("evidence_level", "E0"),
            ]
        )
    return markdown_table(
        ["Fictional competitor", "Price", "Channel", "Positioning", "Key feature", "Content hook", "Evidence"],
        table_rows,
    )


def channel_summary(rows: list[dict[str, str]]) -> str:
    counts = Counter(row.get("channel", "Unspecified") for row in rows)
    return ", ".join(f"{channel}: {count}" for channel, count in counts.items())


def build_user_segments(brief: dict[str, str]) -> list[list[str]]:
    category = brief["category"]
    return [
        [
            "Small-space remote worker",
            f"Wants a compact {category} setup that improves the desk visually.",
            "May worry about clutter, cable visibility, and setup time.",
            "Show footprint, cable routing, and before-after desk reset footage.",
        ],
        [
            "Student creator",
            "Needs an affordable visual upgrade for study clips and casual content.",
            "May worry that lighting controls are complicated.",
            "Use quick setup clips and simple scene presets.",
        ],
        [
            "Gift buyer",
            "Needs a useful desk gift that is easy to understand without exact specs.",
            "May worry about compatibility, returns, and package contents.",
            "Make package contents, setup requirements, and return policy plain.",
        ],
    ]


def build_content_angles(brief: dict[str, str], rows: list[dict[str, str]]) -> list[list[str]]:
    category = brief["category"]
    country = brief["target_country"]
    hooks = [
        [
            "Desk reset transformation",
            "Short-form visual commerce",
            f"Turn a cramped desk into a warmer {category} setup in one quick sequence.",
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
            "Modular layout demo",
            "Short-form visual commerce",
            "Show three rearranged layouts from the same fictional kit.",
            "Needs durability and attachment review.",
        ],
    ]

    for row in rows[:3]:
        hooks.append(
            [
                f"Differentiate from {row.get('brand', 'fictional competitor')}",
                row.get("channel", "Channel test"),
                f"Counter the fixture hook '{row.get('content_hook', 'generic setup content')}' with a clearer use case.",
                "Treat as synthetic competitor observation.",
            ]
        )
    return hooks


def build_channel_strategy(brief: dict[str, str]) -> list[list[str]]:
    return [
        [
            "Short-form visual commerce",
            "Use fast before-after demos and modular layout clips.",
            "Hook rate, save rate, product-page click-through.",
            "Avoid claims that imply guaranteed focus or wellness outcomes.",
        ],
        [
            "Search-led marketplace listing",
            "Start with dimensions, package contents, setup steps, and use cases.",
            "Search conversion, question volume, return reasons.",
            "Confirm all specs before publishing.",
        ],
        [
            "Creator storefront",
            "Ask creators to show honest setup time and desk fit.",
            "Creator click-through, assisted purchases, qualitative objections.",
            "Use fictional demo assumptions only in this repository.",
        ],
    ]


def build_report(
    brief: dict[str, str],
    competitors: list[dict[str, str]],
    rules: dict[str, Any],
    source_policy: dict[str, Any],
    preferences: dict[str, Any],
    input_path: Path,
    competitor_path: Path,
    dry_run: bool,
) -> str:
    prices = [price for price in (parse_price(row.get("price_usd", "")) for row in competitors) if price is not None]
    avg_price = mean(prices) if prices else 0.0
    min_price = min(prices) if prices else 0.0
    max_price = max(prices) if prices else 0.0
    content_rows = build_content_angles(brief, competitors)
    review_prompts = list(rules.get("human_review_prompts", []))
    if not isinstance(review_prompts, list):
        review_prompts = []

    report_audience = (
        preferences.get("report_preferences", {}).get("audience")
        if isinstance(preferences.get("report_preferences"), dict)
        else None
    )
    if not report_audience:
        report_audience = "AI product manager and content growth reviewer"

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
        f"- Intended reader: {report_audience}",
        "",
        "## Executive summary",
        "",
        markdown_table(
            ["Layer", "Output", "Evidence"],
            [
                ["Fact", f"{brief['category']} is tested for {brief['target_country']} at {brief['price_band']}.", "E0 demo fixture"],
                ["Inference", "Visual desk transformation and small-space proof are likely stronger than technical feature lists.", "E4 hypothesis"],
                ["Recommendation", "Run content-first tests while keeping claims conservative and reviewed.", "Requires manual review"],
            ],
        ),
        "",
        "## Target market hypothesis",
        "",
        f"- Category: {brief['category']}",
        f"- Target market: {brief['target_country']}",
        f"- Price band: {brief['price_band']}",
        f"- Primary channels: {brief['primary_channels']}",
        f"- Audience hypothesis: {brief['audience_hypothesis']}",
        "- Core hypothesis: buyers first understand the product through visible setup improvement, not abstract performance claims.",
        f"- Fixture channel coverage: {channel_summary(competitors)}.",
        "",
        "## User segments",
        "",
        markdown_table(
            ["Segment", "Job to be done", "Likely objection", "Content response"],
            build_user_segments(brief),
        ),
        "",
        "## Competitor matrix summary",
        "",
        competitor_matrix(competitors),
        "",
        "## Price band observation",
        "",
        f"- Fictional competitor price range: ${min_price:.0f}-${max_price:.0f}.",
        f"- Fictional average competitor price: ${avg_price:.0f}.",
        f"- Demo read: {brief['price_band']} should support a value-led message while leaving room for packaging, setup proof, and content assets.",
        "- Evidence note: all price points are synthetic and cannot be used as real market benchmarks.",
        "",
        "## Product positioning",
        "",
        markdown_table(
            ["Positioning pillar", "What to say", "What to avoid"],
            [
                ["Compact transformation", "A simple visual desk upgrade for small spaces.", "Unsupported productivity or wellness outcomes."],
                ["Modular setup", "Rearrangeable layout for desks, shelves, and content corners.", "Claims of superior durability without proof."],
                ["Giftable utility", "Easy to understand, easy to set up, and visually satisfying.", "Promises about universal compatibility."],
            ],
        ),
        "",
        "## Content growth angles",
        "",
        markdown_table(
            ["Angle", "Channel", "Hook", "Review needed"],
            content_rows,
        ),
        "",
        "## Channel strategy",
        "",
        markdown_table(
            ["Channel", "Role", "Measure", "Manual review focus"],
            build_channel_strategy(brief),
        ),
        "",
        "## Risk notes",
        "",
        markdown_table(
            ["Risk", "Why it matters", "Mitigation"],
            [
                [
                    "Unsupported performance claims",
                    "Focus, wellness, and productivity claims can be misleading if unverified.",
                    "Use visual and functional claims only; review stronger wording manually.",
                ],
                [
                    "Country-specific compliance gaps",
                    "Lighting products may require labeling, safety, or packaging review.",
                    f"Run a {brief['target_country']} compliance check before real launch use.",
                ],
                [
                    "Synthetic competitor data",
                    "Fixture rows are useful for workflow demonstration, not real competitive strategy.",
                    "Replace with reviewed source logs before production use.",
                ],
                [
                    "Price and shipping assumptions",
                    "The report does not verify landed cost, delivery time, or return policy.",
                    "Confirm costs, fulfillment, warranty, and return language before publishing.",
                ],
            ],
        ),
        "",
        "## Evidence level and manual review notes",
        "",
        "### Source priority",
        "",
        source_policy_table(source_policy, rules),
        "",
        "### Evidence levels",
        "",
        config_table(
            rules,
            "evidence_levels",
            ["Level", "Label", "Confidence", "Allowed use"],
            ["level", "label", "confidence", "allowed_use"],
        ),
        "",
        "### Manual review checklist",
        "",
    ]

    for prompt in review_prompts:
        report_lines.append(f"- {prompt}")

    report_lines.extend(
        [
            "- Confirm all public copy separates facts, inferences, and recommendations.",
            "- Replace synthetic rows with reviewed source logs before real launch decisions.",
            "",
            "## Demo provenance",
            "",
            "- Product and competitor names are fictional.",
            "- Metrics are synthetic and should not be treated as market facts.",
            "- No credentials, private customer data, real company data, or live marketplace data was used.",
        ]
    )

    return "\n".join(report_lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a local-only ecommerce market research report.")
    parser.add_argument("--input", required=True, type=Path, help="Path to product brief markdown.")
    parser.add_argument("--competitors", required=True, type=Path, help="Path to fictional competitor CSV.")
    parser.add_argument("--output", required=True, type=Path, help="Path to write generated markdown report.")
    parser.add_argument("--rules", required=True, type=Path, help="Path to research rules config.")
    parser.add_argument("--sources", type=Path, help="Optional source policy config.")
    parser.add_argument("--preferences", type=Path, help="Optional report preferences config.")
    parser.add_argument("--dry-run", action="store_true", help="Mark output as Safe Demo dry run.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    brief = parse_product_brief(args.input)
    competitors = load_competitors(args.competitors)
    rules = load_config(args.rules)
    source_policy = load_config(args.sources)
    preferences = load_config(args.preferences)

    report = build_report(
        brief=brief,
        competitors=competitors,
        rules=rules,
        source_policy=source_policy,
        preferences=preferences,
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
