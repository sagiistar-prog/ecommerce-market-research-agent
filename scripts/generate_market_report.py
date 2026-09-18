#!/usr/bin/env python3
"""Compatibility CLI for evidence-based local market research."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any
from evidence_analysis import parse_brief, load_rows, analyze, parse_price
from report_renderer import render_report
try:
    import yaml
except ImportError:
    yaml = None

NETWORK_IMPORTS_ARE_INTENTIONALLY_ABSENT = True
parse_product_brief_text = parse_brief
load_competitors_text = load_rows


def load_config(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    raw = path.read_text(encoding="utf-8")
    loaded = yaml.safe_load(raw) if yaml else json.loads(raw)
    return loaded if isinstance(loaded, dict) else {}


def parse_product_brief(path: Path) -> dict[str, str]:
    return parse_brief(path.read_text(encoding="utf-8-sig"))


def load_competitors(path: Path) -> list[dict[str, str]]:
    return load_rows(path.read_text(encoding="utf-8-sig"))


def build_report(brief, competitors, rules, source_policy, preferences, input_path, competitor_path, dry_run) -> str:
    # Legacy configuration arguments remain accepted; evidence is never upgraded by a config.
    return render_report(analyze(brief, competitors))


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
