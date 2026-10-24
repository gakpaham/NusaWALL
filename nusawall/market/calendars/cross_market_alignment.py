from __future__ import annotations


def cross_market_alignment(date_key: str) -> str:
    """Return a standard alignment label for cross-market ordering."""
    return f"aligned::{date_key}"
