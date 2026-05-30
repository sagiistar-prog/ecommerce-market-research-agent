#!/usr/bin/env python3
"""Local web UI server for the ecommerce market research agent."""

from __future__ import annotations

import argparse
import json
import socket
import sys
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import generate_market_report as report_generator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = PROJECT_ROOT / "web"


def load_text(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def find_free_port(preferred_port: int) -> int:
    for port in range(preferred_port, preferred_port + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                probe.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise RuntimeError("No free local port found")


class AgentRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def log_message(self, format: str, *args) -> None:  # noqa: A002 - inherited API name
        sys.stdout.write("%s - %s\n" % (self.log_date_time_string(), format % args))
        sys.stdout.flush()

    def send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}

    def do_GET(self) -> None:  # noqa: N802 - inherited API name
        if self.path == "/api/sample":
            self.send_json(
                {
                    "brief": load_text("examples/sample_product_brief.md"),
                    "competitors": load_text("examples/sample_competitor_table.csv"),
                }
            )
            return
        return super().do_GET()

    def do_POST(self) -> None:  # noqa: N802 - inherited API name
        if self.path != "/api/generate":
            self.send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint")
            return

        try:
            payload = self.read_json()
            brief_text = str(payload.get("brief", "")).strip()
            competitor_csv = str(payload.get("competitors", "")).strip()
            if not brief_text or not competitor_csv:
                self.send_json(
                    {"error": "Product brief and competitor CSV are required."},
                    HTTPStatus.BAD_REQUEST,
                )
                return

            rules = report_generator.load_config(PROJECT_ROOT / "configs/research_rules.yaml")
            source_policy = report_generator.load_config(PROJECT_ROOT / "configs/source_policy.yaml")
            preferences = report_generator.load_config(PROJECT_ROOT / "configs/user_preferences.yaml")
            brief = report_generator.parse_product_brief_text(brief_text)
            competitors = report_generator.load_competitors_text(competitor_csv)
            markdown = report_generator.build_report(
                brief=brief,
                competitors=competitors,
                rules=rules,
                source_policy=source_policy,
                preferences=preferences,
                input_path=Path("web-ui/product_brief.md"),
                competitor_path=Path("web-ui/competitor_table.csv"),
                dry_run=True,
            )
            self.send_json({"report": markdown})
        except Exception as exc:  # pragma: no cover - surfaced to local UI
            self.send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local web UI for the market research agent.")
    parser.add_argument("--host", default="127.0.0.1", help="Local bind host.")
    parser.add_argument("--port", default=8765, type=int, help="Preferred local port.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    port = find_free_port(args.port)
    server = ThreadingHTTPServer((args.host, port), AgentRequestHandler)
    print(f"Local app running at http://{args.host}:{port}", flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
