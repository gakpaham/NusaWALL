#!/usr/bin/env python
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"


def get_venv_python() -> Path:
    if sys.platform.startswith("win"):
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def ensure_environment() -> Path:
    if not VENV_DIR.exists():
        print("[NusaWall] Creating virtual environment in .venv...")
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)

    python_path = get_venv_python()
    if not python_path.exists():
        raise FileNotFoundError(f"Virtual environment Python was not found at {python_path}")
    return python_path


def install_project(python_path: Path) -> None:
    print("[NusaWall] Installing project dependencies...")
    subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(python_path), "-m", "pip", "install", "-e", "."], cwd=str(ROOT), check=True)


def cmd_setup() -> None:
    python_path = ensure_environment()
    install_project(python_path)
    print("\n[NusaWall] Setup complete.")
    print("No activation is required. Use the virtual environment's Python directly:")
    print(f"{python_path} manage.py analyze AAPL")


def cmd_doctor() -> None:
    print("NusaWall environment check:")
    try:
        import nusawall  # noqa: F401
        print("Package import: OK")
    except Exception as exc:  # pragma: no cover - diagnostic command
        print(f"Package import: FAIL ({exc})")
        raise


def cmd_status() -> None:
    print("NusaWall command runner ready.")
    print(f"Project root: {ROOT}")
    print(f"Virtual environment: {VENV_DIR}")


def cmd_analyze(ticker: str, question: str, period: str) -> None:
    from nusawall.llm.market_analysis import analyze_stock

    try:
        result = analyze_stock(ticker, question=question, period=period)
    except (ValueError, RuntimeError) as exc:
        print(f"[NusaWall] Analysis failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    print(result)
    print("\nNote: This information is for research purposes only and is not financial advice.")


def cmd_run() -> None:
    print("NusaWall does not install dependencies when you run it.")
    print("One-time Python setup: python manage.py setup")
    print("Analyze a ticker:    python manage.py analyze AAPL")
    print("Open the web app:    python manage.py web")


def cmd_web(host: str, port: int) -> None:
    from nusawall.web.server import serve

    try:
        serve(host, port)
    except OSError as exc:
        print(f"[NusaWall] Could not start the web server: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


def main() -> None:
    parser = argparse.ArgumentParser(prog="manage.py", description="NusaWall project CLI")
    parser.add_argument(
        "command",
        nargs="?",
        default="run",
        choices=["run", "start", "setup", "doctor", "status", "analyze", "web"],
        help="Command to set up, analyze a ticker, or start the local web app.",
    )
    parser.add_argument("ticker", nargs="?", help="Stock ticker, for example BBCA.JK or AAPL.")
    parser.add_argument(
        "--question",
        default=(
            "Analyze this stock using the available data. Explain the trend, "
            "observable risks, and what to monitor next."
        ),
        help="Focus for the built-in market analysis.",
    )
    parser.add_argument("--period", default="6mo", help="Yahoo Finance history period (default: 6mo).")
    parser.add_argument("--host", default="127.0.0.1", help="Web server host (default: 127.0.0.1).")
    parser.add_argument("--port", type=int, default=8000, help="Web server port (default: 8000).")
    args = parser.parse_args()

    command = args.command
    if command in {"run", "start", "setup"}:
        cmd_setup() if command == "setup" else cmd_run()
    elif command == "analyze":
        if not args.ticker:
            parser.error("the analyze command requires a ticker, for example: analyze BBCA.JK")
        cmd_analyze(args.ticker, args.question, args.period)
    elif command == "doctor":
        cmd_doctor()
    elif command == "web":
        cmd_web(args.host, args.port)
    else:
        cmd_status()


if __name__ == "__main__":
    main()
