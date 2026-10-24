from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent


def lint() -> None:
    print(f"Linting {ROOT}")


def test() -> None:
    print(f"Running tests in {ROOT}")
