from __future__ import annotations

import io
import json
from unittest.mock import MagicMock

import manage
from nusawall.web import server as web_server


class StubRequestHandler(web_server.RequestHandler):
    def __init__(self, method, path, payload=None):
        body = json.dumps(payload).encode("utf-8") if payload is not None else b""
        self.command = method
        self.path = path
        self.headers = {"Content-Length": str(len(body))}
        self.rfile = io.BytesIO(body)
        self.wfile = io.BytesIO()
        self.status = None
        self.response_headers = {}

    def send_response(self, status, message=None):
        self.status = status

    def send_header(self, keyword, value):
        self.response_headers[keyword] = value

    def end_headers(self):
        pass


def request(method, path, payload=None):
    handler = StubRequestHandler(method, path, payload)
    getattr(handler, f"do_{method.upper()}")()
    return handler.status, handler.response_headers, handler.wfile.getvalue()


def test_homepage_serves_local_interface():
    status, headers, body = request("GET", "/")

    assert status == 200
    assert headers["Content-Type"] == "text/html; charset=utf-8"
    assert b'<html lang="id">' in body
    assert b"Analisis pasar" in body
    assert b"NusaWall" in body


def test_analysis_endpoint_calls_existing_analysis(monkeypatch):
    analyze = MagicMock(return_value="A summary of the trend and risks.")
    monkeypatch.setattr(web_server, "analyze_stock", analyze)

    status, headers, body = request(
        "POST",
        "/api/analyze",
        {
            "ticker": " bbca.jk ",
            "question": "Analyze the trend",
            "period": "1y",
        },
    )

    assert status == 200
    assert headers["Content-Type"] == "application/json; charset=utf-8"
    assert json.loads(body) == {
        "answer": "A summary of the trend and risks.",
        "ticker": "BBCA.JK",
        "engine": "NusaWall Online Learner",
    }
    analyze.assert_called_once_with(
        "bbca.jk",
        question="Analyze the trend",
        period="1y",
    )


def test_analysis_endpoint_rejects_invalid_period():
    status, _, body = request(
        "POST",
        "/api/analyze",
        {"ticker": "AAPL", "period": "not-a-period"},
    )

    assert status == 400
    assert "data period" in json.loads(body)["error"]


def test_analysis_endpoint_returns_analysis_errors(monkeypatch):
    def fail_analysis(*args, **kwargs):
        raise RuntimeError("Yahoo Finance is unavailable.")

    monkeypatch.setattr(web_server, "analyze_stock", fail_analysis)
    status, _, body = request(
        "POST",
        "/api/analyze",
        {"ticker": "AAPL"},
    )

    assert status == 502
    assert json.loads(body)["error"] == "Yahoo Finance is unavailable."


def test_web_command_uses_requested_host_and_port(monkeypatch):
    called = {}
    monkeypatch.setattr(
        "nusawall.web.server.serve",
        lambda host, port: called.update(host=host, port=port),
    )
    monkeypatch.setattr("sys.argv", ["manage.py", "web", "--host", "localhost", "--port", "9001"])

    manage.main()

    assert called == {"host": "localhost", "port": 9001}
