"""Render the same structured analysis used by the plugin and browser."""
from __future__ import annotations

import html

from evidence_analysis import BRIEF_LABELS


def text(value) -> str:
    if value is None or value == "":
        return "Not provided"
    value = html.escape(str(value), quote=False).replace("\n", " ").replace("\r", " ").replace("·", " ")
    for char in "|*`_[]\\":
        value = value.replace(char, f"&#{ord(char)};")
    return value


def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |",
                      *("| " + " | ".join(text(cell) for cell in row) + " |" for row in rows)])


def render_report(analysis: dict) -> str:
    sample = analysis["sample"]
    lines = ["# Market research review", "",
             "## Decision snapshot", "",
             "Clarify the brief before drawing conclusions." if analysis["decision_status"] == "needs_input" else "Use this review to plan research. The supplied sample does not establish a launch decision.", "",
             f'{sample["observation_count"]} observations; {sample["priced_count"]} prices supplied; {sample["synthetic_count"]} synthetic rows; {sample["source_date_count"]} rows with a source and capture date.', "",
             "## Product question", "",
             table(["Brief field", "Supplied value"], [[label, analysis["brief"][key]] for key, label in BRIEF_LABELS.items()]), "",
             "## What the sample shows", ""]
    lines.extend(f'- {item["id"]}: {text(item["text"])} [{", ".join(item["evidence_ids"])}]' for item in analysis["observations"])
    lines.extend(["", "## Comparable prices", "", "USD offer prices, grouped by the submitter. Missing prices remain missing. Groups do not include ungrouped observations.", ""])
    if sample["price_groups"]:
        lines.append(table(["Group", "Data", "Priced / total", "Min USD", "Median USD", "Mean USD", "Max USD", "Rows"], [
            [group["group"], group["data_kind"], f'{group["priced_count"]} / {group["observation_count"]}',
             *[f'{group[key]:.2f}' if group[key] is not None else None for key in ("minimum_usd", "median_usd", "mean_usd", "maximum_usd")],
             ", ".join(group["evidence_ids"])] for group in sample["price_groups"]]))
    else:
        lines.append("No comparable groups supplied. Assign comparison_group after checking the offer basis; individual prices remain visible below.")
    lines.extend(["", "## Next research actions", ""])
    for task in analysis["research_tasks"]:
        lines.extend([f'### {task["id"]} / {task["priority"].capitalize()}: {text(task["question"])}', "",
                      text(task["action"]), "", f'Completion evidence: {text(task["success_signal"])}', "",
                      "Basis: " + (", ".join(task["evidence_ids"]) if task["evidence_ids"] else "Submitted brief or missing brief fields"), ""])
    lines.extend(["## Evidence ledger", "", "IDs identify input observations, not independent verified sources. Repeated brand or source entries may not be independent.", ""])
    for item in analysis["evidence"]:
        lines.extend([f'### {item["id"]} / {text(item["brand"])}', "", table(["Field", "Submitted value"], [
            ["Price USD", f'{item["price_usd"]:.2f}' if item["price_usd"] is not None else None],
            ["Channel", item["channel"]], ["Positioning claim", item["positioning_claim"]], ["Key feature", item["key_feature"]],
            ["Content hook", item["content_hook"]], ["Comparison group", item["comparison_group"]],
            ["Data kind", item["data_kind"]], ["Declared evidence level", item["declared_evidence_level"]],
            ["Source URL (not fetched)", item["source_url"]], ["Observed at", item["observed_at"]], ["Notes", item["notes"]],
        ]), ""])
    lines.extend(["## Original brief", "", *[text(line) for line in analysis["original_brief"].splitlines() if line.strip()], "",
                  "## Interpretation limits", "", *[f'- {line}' for line in analysis["limitations"]], ""])
    return "\n".join(lines)
