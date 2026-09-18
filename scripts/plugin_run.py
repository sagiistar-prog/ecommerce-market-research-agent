#!/usr/bin/env python3
"""Versioned, offline JSON interface. No network or model calls."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
MAX_BYTES = 1_000_000

def execute(data: dict) -> dict:
    from evidence_analysis import parse_brief, load_rows, analyze
    from report_renderer import render_report
    analysis = analyze(parse_brief(data["brief"]), load_rows(data["competitors_csv"]))
    return {"markdown": render_report(analysis), "competitor_count": len(analysis["evidence"]), "manual_review_required": True, "analysis": analysis}


def run(data: dict) -> dict:
    from jsonschema import Draft202012Validator
    schema = json.loads((ROOT / "schemas/input.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(data)
    result = {"schema_version": "2.0", "status": "ok", "mode": "local_evidence_analysis", "result": execute(data), "warnings": ["Only submitted observations are analyzed; source URLs are not fetched or verified.", "Evidence levels and comparison groups are supplied labels, not verified market facts."]}
    Draft202012Validator(json.loads((ROOT / "schemas/output.schema.json").read_text(encoding="utf-8"))).validate(result)
    return result

def main() -> int:
    parser = argparse.ArgumentParser(description='将产品简述与竞品表整理成证据分级研究草稿')
    parser.add_argument("--input", type=Path, help="UTF-8 JSON file. Omit to read stdin.")
    parser.add_argument("--output-dir", type=Path, help="New directory inside output/. Existing directories are never overwritten.")
    args = parser.parse_args()
    try:
        if args.input and args.input.stat().st_size > MAX_BYTES: raise ValueError("Input exceeds 1 MB")
        raw = args.input.read_text(encoding="utf-8-sig") if args.input else sys.stdin.buffer.read(MAX_BYTES + 1).decode("utf-8-sig")
        if len(raw.encode("utf-8")) > MAX_BYTES: raise ValueError("Input exceeds 1 MB")
        data = json.loads(raw, parse_constant=lambda value: (_ for _ in ()).throw(ValueError("Non-finite JSON number")))
        payload = run(data)
        if args.output_dir:
            destination = args.output_dir.resolve()
            allowed = (ROOT / "output").resolve()
            if not destination.is_relative_to(allowed) or destination == allowed:
                raise ValueError("Choose a new subdirectory inside output/")
            destination.mkdir(parents=True, exist_ok=False)
            (destination / "result.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            (destination / "result.md").write_text(payload["result"]["markdown"], encoding="utf-8")
            if "csv" in payload["result"]: (destination / "timeline.csv").write_text(payload["result"]["csv"], encoding="utf-8")
        code = 0
    except ImportError:
        payload = {"schema_version":"2.0", "status":"error", "error":{"code":"DEPENDENCY_MISSING", "message":"Install requirements-plugin.txt before running the plugin."}}
        code = 2
    except Exception as exc:
        # Do not echo user text, stack traces or local file paths into the response.
        if type(exc).__name__ == "ValidationError":
            location = ".".join(str(part) for part in exc.absolute_path) or "input"
            message = f"Invalid field: {location}; failed {exc.validator} constraint. See schemas/input.schema.json."
        elif isinstance(exc, (FileExistsError, FileNotFoundError, PermissionError, OSError)):
            message = "Cannot read input or create a fresh output directory. Existing output is preserved."
        elif isinstance(exc, json.JSONDecodeError): message = "Input must be valid UTF-8 JSON."
        else: message = str(exc) if isinstance(exc, ValueError) else "Generation failed; check the documented input contract."
        payload = {"schema_version":"2.0", "status":"error", "error":{"code":"INVALID_INPUT_OR_OUTPUT", "message":message}}
        code = 2
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, allow_nan=False))
    return code

if __name__ == "__main__":
    raise SystemExit(main())
