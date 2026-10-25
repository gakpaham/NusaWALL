from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from nusawall.llm.market_analysis import ANALYTICS_ENGINE, DEFAULT_QUESTION, analyze_stock


STATIC_DIR = Path(__file__).resolve().parent / "static"
MAX_REQUEST_BYTES = 16_384
MAX_QUESTION_LENGTH = 2_000
VALID_PERIODS = {"1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"}


class NusaWallHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class RequestHandler(BaseHTTPRequestHandler):
    server_version = "NusaWall/0.1"

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path == "/":
            self._serve_static("index.html", "text/html; charset=utf-8")
        elif path == "/styles.css":
            self._serve_static("styles.css", "text/css; charset=utf-8")
        elif path == "/app.js":
            self._serve_static("app.js", "text/javascript; charset=utf-8")
        else:
            self._send_json(404, {"error": "Page not found."})

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/api/analyze":
            self._send_json(404, {"error": "Endpoint not found."})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, {"error": "Invalid request content length."})
            return
        if content_length <= 0 or content_length > MAX_REQUEST_BYTES:
            self._send_json(413, {"error": "Request is empty or too large."})
            return

        try:
            payload = json.loads(self.rfile.read(content_length))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "Request body must contain valid JSON."})
            return
        if not isinstance(payload, dict):
            self._send_json(400, {"error": "Request body must be a JSON object."})
            return

        ticker = payload.get("ticker")
        question = payload.get("question", DEFAULT_QUESTION)
        period = payload.get("period", "6mo")
        if not isinstance(ticker, str) or not ticker.strip() or len(ticker) > 30:
            self._send_json(400, {"error": "Enter a valid stock ticker, such as BBCA.JK."})
            return
        if not isinstance(question, str) or not question.strip() or len(question) > MAX_QUESTION_LENGTH:
            self._send_json(
                400,
                {"error": f"Question must contain 1–{MAX_QUESTION_LENGTH} characters."},
            )
            return
        if not isinstance(period, str) or period not in VALID_PERIODS:
            self._send_json(400, {"error": "The selected data period is invalid."})
            return
        try:
            answer = analyze_stock(
                ticker.strip(),
                question=question.strip(),
                period=period,
            )
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        except RuntimeError as exc:
            self._send_json(502, {"error": str(exc)})
            return

        self._send_json(
            200,
            {
                "answer": answer,
                "ticker": ticker.strip().upper(),
                "engine": ANALYTICS_ENGINE,
            },
        )

    def _serve_static(self, filename: str, content_type: str) -> None:
        try:
            content = (STATIC_DIR / filename).read_bytes()
        except OSError as exc:
            self.log_error("Could not read web interface file %s: %s", filename, exc)
            self._send_json(500, {"error": "The interface file could not be read."})
            return

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; connect-src 'self';")
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)


def create_server(host: str = "127.0.0.1", port: int = 8000) -> NusaWallHTTPServer:
    """Create the local web server without starting its request loop."""
    return NusaWallHTTPServer((host, port), RequestHandler)


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Run the NusaWall browser interface until interrupted."""
    server = create_server(host, port)
    print(f"NusaWall is available at http://{host}:{server.server_port}")
    print("Native market analytics are built in; Yahoo Finance data requires internet access.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nNusaWall server stopped.")
    finally:
        server.server_close()
