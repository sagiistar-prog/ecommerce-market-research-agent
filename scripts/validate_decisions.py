#!/usr/bin/env python3
"""Validate host-authored hypotheses against an exact local evidence snapshot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, ValidationError
from evidence_analysis import analysis_digest

ROOT = Path(__file__).resolve().parents[1]


def validate(analysis: dict, decisions: dict) -> dict:
    output_schema = json.loads((ROOT / "schemas/output.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(output_schema["$defs"]["analysis"]).validate(analysis)
    schema = json.loads((ROOT / "schemas/decisions.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(decisions)
    if analysis["analysis_id"] != analysis_digest(analysis):
        raise ValueError("Evidence snapshot changed after analysis; generate it again")
    if decisions["analysis_id"] != analysis["analysis_id"]:
        raise ValueError("Decisions refer to a different analysis; review the current evidence")
    records = {item["id"]: item for item in analysis["evidence"]}
    records["BRIEF"] = {"original_brief": analysis["original_brief"]}
    citations = 0
    for index, proposal in enumerate(decisions["proposals"], start=1):
        for ref in proposal["evidence"]:
            record = records.get(ref["id"])
            if record is None or ref["field"] not in record:
                raise ValueError(f"Proposal {index}: citation does not resolve to an allowed input field")
            original = record[ref["field"]]
            if not isinstance(original, str) or ref["quote"] not in original:
                raise ValueError(f"Proposal {index}: quoted text does not occur in the cited field")
            citations += 1
    return {"status": "ok", "scope": "reference_validation_only", "proposal_count": len(decisions["proposals"]),
            "citation_count": citations, "analysis_id": analysis["analysis_id"],
            "manual_review_required": True}


def read_json(path: Path) -> dict:
    if path.stat().st_size > 2_000_000:
        raise ValueError("Input file exceeds 2 MB")
    return json.loads(path.read_text(encoding="utf-8-sig"), parse_constant=lambda value: (_ for _ in ()).throw(ValueError("JSON numbers must be finite")))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", required=True, type=Path)
    parser.add_argument("--decisions", required=True, type=Path)
    args = parser.parse_args()
    try:
        payload = read_json(args.analysis)
        if not isinstance(payload, dict):
            raise ValueError("Analysis must be a JSON object")
        analysis = payload.get("result", payload).get("analysis")
        result = validate(analysis, read_json(args.decisions))
        code = 0
    except ValidationError as exc:
        result = {"status": "error", "message": f"Invalid field: {'.'.join(str(p) for p in exc.absolute_path) or 'input'} ({exc.validator})"}
        code = 2
    except (ValueError, OSError, AttributeError, TypeError) as exc:
        result = {"status": "error", "message": str(exc) if isinstance(exc, ValueError) and not isinstance(exc, json.JSONDecodeError) else "Check the JSON input and readable file paths"}
        code = 2
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
