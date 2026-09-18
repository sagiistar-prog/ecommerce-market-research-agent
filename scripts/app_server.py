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

from jsonschema import ValidationError
from plugin_run import run
from hypothesis_review import prepare_review, export_review


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
        limit=4_000_000 if self.path in {'/api/decisions','/api/review'} else 1_000_000
        if not 0 < length <= limit:
            raise ValueError(f"Request body must contain 1 to {limit} bytes")
        raw = self.rfile.read(length).decode("utf-8")
        parsed = json.loads(raw, parse_constant=lambda value: (_ for _ in ()).throw(ValueError("JSON numbers must be finite")))
        if not isinstance(parsed, dict): raise ValueError("Request must be a JSON object")
        return parsed

    def do_GET(self) -> None:  # noqa: N802 - inherited API name
        if self.path == "/api/sample-csv":
            body = load_text("examples/sample_competitor_table.csv").encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="competitor-template.csv"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/api/sample":
            fixture=json.loads(load_text("examples/pet-bowl-input.json"))
            self.send_json(
                {
                    "brief": fixture['brief'],
                    "competitors": fixture['competitors_csv'],
                }
            )
            return
        if self.path == "/api/sample-decisions":
            self.send_json(json.loads(load_text("examples/pet-bowl-decisions.json")))
            return
        return super().do_GET()

    def do_POST(self) -> None:  # noqa: N802 - inherited API name
        expected = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
        origin = self.headers.get("Origin")
        if self.headers.get("Host") not in expected or (origin and origin not in {f"http://{h}" for h in expected}):
            self.send_json({"error": "Origin rejected"}, status=403)
            return
        if self.path not in {"/api/generate", "/api/decisions", "/api/review"}:
            self.send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint")
            return

        try:
            payload = self.read_json()
            if self.path in {"/api/decisions", "/api/review"}:
                allowed={"analysis","decisions"} | ({"review"} if self.path=="/api/review" else set())
                if set(payload)!=allowed:
                    raise ValueError('Provide the current analysis and hypothesis package, with review choices when exporting.')
                if self.path=="/api/decisions":
                    self.send_json({'review':prepare_review(payload['analysis'],payload['decisions'])})
                else:
                    self.send_json(export_review(payload['analysis'],payload['decisions'],payload['review']))
                return
            if set(payload) - {"brief", "competitors"}:
                raise ValueError("Only brief and competitors fields are accepted")
            result = run({"brief": payload.get("brief"), "competitors_csv": payload.get("competitors")})["result"]
            self.send_json({"report": result["markdown"], "analysis": result["analysis"]})
        except ValidationError as exc:
            field = ".".join(str(part) for part in exc.absolute_path) or "input"
            self.send_json({"error": f"Check {field}: expected text within the documented length limit."}, HTTPStatus.BAD_REQUEST)
        except (ValueError, UnicodeError) as exc:
            self.send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        except Exception:
            self.send_json({"error": "Analysis failed. Your inputs are preserved; check the local server installation."}, HTTPStatus.INTERNAL_SERVER_ERROR)


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
