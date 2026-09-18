"""Deterministic analysis of submitted observations, without network or model calls."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import defaultdict
from datetime import date
from io import StringIO
from statistics import mean, median
from urllib.parse import urlsplit

REQUIRED_COLUMNS = {
    "brand", "price_usd", "channel", "positioning_claim", "key_feature",
    "content_hook", "evidence_level", "notes",
}
OPTIONAL_COLUMNS = {"source_url", "observed_at", "comparison_group", "data_kind"}
BRIEF_LABELS = {
    "category": "Category", "target_country": "Target market", "price_band": "Target price",
    "primary_channels": "Intended channels", "audience_hypothesis": "Audience hypothesis",
    "research_goal": "Decision question", "positioning_note": "Positioning hypothesis", "constraints": "Constraints",
}


def analysis_digest(analysis: dict) -> str:
    content = {key: value for key, value in analysis.items() if key != "analysis_id"}
    return "sha256:" + hashlib.sha256(json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()
ALIASES = {
    "品类": "category", "产品品类": "category", "target_market": "target_country", "目标市场": "target_country",
    "目标国家": "target_country", "价格带": "price_band", "目标价格": "price_band",
    "渠道": "primary_channels", "主要渠道": "primary_channels", "目标用户": "audience_hypothesis",
    "用户假设": "audience_hypothesis", "研究问题": "research_goal", "研究目标": "research_goal",
    "定位假设": "positioning_note", "定位": "positioning_note", "约束": "constraints",
}


def parse_brief(text: str) -> dict[str, str]:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Product brief is required")
    if len(text) > 30_000:
        raise ValueError("Product brief exceeds 30000 characters")
    fields = {"raw_text": text.strip()}
    for line in text.splitlines():
        clean = re.sub(r"^\s*(?:[-*]\s+|#{1,6}\s+)?", "", line).strip()
        # Both **Category:** and **Category**: are accepted, as are Chinese labels.
        match = re.match(r"(.{1,50}?)[：:]\s*(.*)$", clean)
        if not match:
            continue
        label = re.sub(r"[\s/-]+", "_", match[1].replace("**", "").strip().lower())
        key = ALIASES.get(label, label)
        value = match[2].removeprefix("**").strip()
        if key in BRIEF_LABELS and value:
            if key in fields and fields[key] != value:
                raise ValueError(f"Conflicting brief values for {key}; keep one value")
            fields[key] = value
    return fields


def parse_price(value: str) -> float | None:
    if not value.strip():
        return None
    try:
        price = float(value)
    except (ValueError, OverflowError):
        raise ValueError("price_usd must be a number such as 19.95, without currency symbols") from None
    if not math.isfinite(price) or not 0 <= price <= 999999999.99:
        raise ValueError("price_usd must be finite and between 0 and 999999999.99")
    return price


def load_rows(text: str) -> list[dict[str, str]]:
    if not isinstance(text, str) or len(text) > 100_000:
        raise ValueError("Competitor CSV must be text with at most 100000 characters")
    reader = csv.DictReader(StringIO(text.lstrip("\ufeff")), strict=True)
    headers = reader.fieldnames or []
    if len(headers) != len(set(headers)):
        raise ValueError("Duplicate CSV column names; each header must appear once")
    missing = REQUIRED_COLUMNS - set(headers)
    unknown = set(headers) - REQUIRED_COLUMNS - OPTIONAL_COLUMNS
    if missing:
        raise ValueError("Missing competitor CSV columns: " + ", ".join(sorted(missing)))
    if unknown:
        raise ValueError("Unknown competitor CSV columns: " + ", ".join(sorted(unknown)))
    rows, seen = [], set()
    try:
        for number, row in enumerate(reader, start=1):
            if number > 250:
                raise ValueError("Keep at most 250 observations per research run")
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"Observation {number}: column count does not match header")
            row = {key: value.strip() for key, value in row.items()}
            if not row["brand"]:
                raise ValueError(f"Observation {number}: brand is required")
            if any(len(value) > 3000 for value in row.values()):
                raise ValueError(f"Observation {number}: each cell must be at most 3000 characters")
            try:
                parse_price(row["price_usd"])
            except ValueError as exc:
                raise ValueError(f"Observation {number}: {exc}") from None
            if row["evidence_level"] not in {"", "E0", "E1", "E2", "E3", "E4"}:
                raise ValueError(f"Observation {number}: evidence_level must be E0 to E4 or blank")
            kind = row.get("data_kind", "")
            if kind not in {"", "synthetic", "provided"}:
                raise ValueError(f"Observation {number}: data_kind must be synthetic, provided or blank")
            if row["evidence_level"] == "E0" and kind == "provided":
                raise ValueError(f"Observation {number}: E0 is synthetic; use data_kind synthetic")
            if row.get("observed_at"):
                try:
                    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["observed_at"]):
                        raise ValueError()
                    if date.fromisoformat(row["observed_at"]) > date.today():
                        raise ValueError()
                except ValueError:
                    raise ValueError(f"Observation {number}: observed_at must be a non-future YYYY-MM-DD date") from None
            if row.get("source_url"):
                try:
                    url = urlsplit(row["source_url"])
                    if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password or re.search(r"\s", row["source_url"]):
                        raise ValueError()
                except ValueError:
                    raise ValueError(f"Observation {number}: source_url must be an HTTP(S) URL without credentials") from None
            fingerprint = tuple(row.get(key, "") for key in sorted(REQUIRED_COLUMNS | OPTIONAL_COLUMNS))
            if fingerprint in seen:
                raise ValueError(f"Observation {number}: duplicate observation; remove it to avoid double counting")
            seen.add(fingerprint)
            rows.append(row)
    except csv.Error:
        raise ValueError("Malformed CSV quoting; quote cells containing commas and close every quote") from None
    if not rows:
        raise ValueError("Add at least one competitor observation below the CSV header")
    return rows


def analyze(brief: dict[str, str], rows: list[dict[str, str]]) -> dict:
    evidence = []
    for index, row in enumerate(rows, start=1):
        evidence.append({
            "id": f"E{index:03d}", "observation_number": index,
            **{key: row[key] for key in ("brand", "channel", "positioning_claim", "key_feature", "content_hook", "notes")},
            "price_usd": parse_price(row["price_usd"]),
            "declared_evidence_level": row["evidence_level"] or None,
            "data_kind": "synthetic" if row["evidence_level"] == "E0" else row.get("data_kind") or "unspecified",
            **{key: row.get(key) or None for key in ("source_url", "observed_at", "comparison_group")},
        })
    channels, groups = defaultdict(list), defaultdict(list)
    for item in evidence:
        channels[item["channel"] or "Unspecified"].append(item["id"])
        if item["comparison_group"]:
            groups[(item["comparison_group"], item["data_kind"])].append(item)
    prices = []
    for (label, kind), items in sorted(groups.items()):
        priced = [item for item in items if item["price_usd"] is not None]
        values = [item["price_usd"] for item in priced]
        prices.append({"group": label, "data_kind": kind, "observation_count": len(items), "priced_count": len(values),
                       "minimum_usd": min(values) if values else None, "maximum_usd": max(values) if values else None,
                       "mean_usd": round(mean(values), 2) if values else None,
                       "median_usd": round(median(values), 2) if values else None,
                       "evidence_ids": [item["id"] for item in priced]})
    channel_counts = [{"channel": label, "count": len(ids), "evidence_ids": ids} for label, ids in sorted(channels.items())]
    observations = []
    for group in prices:
        if group["priced_count"]:
            observations.append({"id": f"O{len(observations)+1:03d}", "kind": "sample_price",
                "text": f'{group["group"]} ({group["data_kind"]}): {group["priced_count"]} submitted prices, USD {group["minimum_usd"]:.2f} to {group["maximum_usd"]:.2f}, median USD {group["median_usd"]:.2f}.',
                "evidence_ids": group["evidence_ids"]})
    for channel in channel_counts:
        observations.append({"id": f"O{len(observations)+1:03d}", "kind": "sample_coverage",
            "text": f'{channel["channel"]}: {channel["count"]} submitted observation' + ("s." if channel["count"] != 1 else "."),
            "evidence_ids": channel["evidence_ids"]})
    for field in ("key_feature", "positioning_claim"):
        repeats = defaultdict(list)
        for item in evidence:
            if item[field]:
                repeats[item[field]].append(item["id"])
        for label, ids in repeats.items():
            if len(ids) > 1:
                observations.append({"id": f"O{len(observations)+1:03d}", "kind": "repeated_claim",
                    "text": f'Submitted {field}: "{label}" appears in {len(ids)} observations. Repetition is not proof of performance or market saturation.', "evidence_ids": ids})

    tasks = []

    def task(priority, question, action, signal, refs):
        tasks.append({"id": f"T{len(tasks)+1:03d}", "priority": priority, "question": question,
                      "action": action, "success_signal": signal, "evidence_ids": refs})

    missing_fields = [key for key in ("category", "target_country", "audience_hypothesis", "research_goal") if not brief.get(key)]
    if missing_fields:
        task("first", "What decision should this research support?",
             "Add labeled brief fields: " + ", ".join(BRIEF_LABELS[key] for key in missing_fields) + ". Keep the original free text as context.",
             "A named user, market and decision that can change after evidence is collected.", [])
    incomplete = [item["id"] for item in evidence if item["data_kind"] != "provided" or not item["source_url"] or not item["observed_at"] or item["declared_evidence_level"] not in {"E1", "E2", "E3"}]
    if incomplete:
        task("first", "Which observations can support the decision?",
             "Before a real product decision, replace synthetic or unspecified rows with permitted observations. Add a source link, capture date and evidence level. For a fictional exercise, keep the limitation explicit without collecting live data.",
             "For real decisions, each relevant observation has a traceable source and date. For fictional exercises, preserve synthetic labels and explain what remains unverified.", incomplete)
    ungrouped = [item["id"] for item in evidence if not item["comparison_group"]]
    if ungrouped:
        task("later", "Optional price comparison: are these offers comparable?",
             "If pricing is part of your decision, assign comparison_group after checking product type, pack size, market, date, shipping and tax treatment. Otherwise keep ungrouped prices as observations.",
             "Each group describes one comparable offer basis; different pack sizes stay separate.", ungrouped)
    missing_prices = [item["id"] for item in evidence if item["price_usd"] is None]
    if missing_prices:
        task("later", "Optional price coverage: what prices are missing?", "If pricing is part of your decision, collect missing USD offer prices with their source and date. Keep unavailable prices blank; they do not block a non-pricing research exercise.",
             "Missing prices are resolved or explicitly excluded; none is substituted with zero.", missing_prices)
    audience = brief.get("audience_hypothesis")
    if audience:
        task("next", f"Does the proposed audience need {brief.get('category', 'this product')}?",
             f"Recruit people matching the supplied hypothesis: {audience}. Ask about their last relevant purchase, current workaround and unmet need before showing the product.",
             "Record concrete past behavior and disconfirming cases. Set the decision threshold before interviews; do not present this audience as a validated persona.", [])
    claims = [item for item in evidence if item["content_hook"] or item["positioning_claim"]]
    if claims:
        task("later", "Which promise should be tested first?",
             "Choose a cited competitor promise and compare it with a product-specific alternative supported by your own evidence. Keep audience, channel and offer fixed; specify the conversion event, sample size and stop rule before testing.",
             "A recorded test outcome with denominator, uncertainty and a decision. A catchy hook alone does not establish demand or a unique advantage.", [item["id"] for item in claims])
    tasks.sort(key=lambda item: {"first": 0, "next": 1, "later": 2}[item["priority"]])
    for index, item in enumerate(tasks, start=1):
        item["id"] = f"T{index:03d}"
    result = {
        "brief": {key: brief.get(key) for key in BRIEF_LABELS}, "original_brief": brief["raw_text"],
        "decision_status": "needs_input" if missing_fields else "research_only",
        "sample": {"observation_count": len(evidence), "priced_count": len(evidence)-len(missing_prices),
                   "missing_price_count": len(missing_prices), "ungrouped_count": len(ungrouped),
                   "synthetic_count": sum(item["data_kind"] == "synthetic" for item in evidence),
                   "source_date_count": sum(bool(item["source_url"] and item["observed_at"]) for item in evidence),
                   "price_groups": prices, "channel_counts": channel_counts},
        "evidence": evidence, "observations": observations, "research_tasks": tasks,
        "limitations": ["Only submitted observations are analyzed; sources and claims are not independently verified.",
                        "Comparison groups and evidence levels are declared by the submitter. They do not establish truth, demand, market share or a launch price.",
                        "Synthetic and provided data may coexist. Review each cited observation before using an aggregate.",
                        "No network requests or language-model calls run in this analyzer. Domain interpretation belongs to the host assistant or researcher."],
    }
    result["analysis_id"] = analysis_digest(result)
    return result
