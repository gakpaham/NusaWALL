from __future__ import annotations


def normalize_number(value: str) -> float:
    cleaned = value.replace(".", "").replace(",", ".")
    return float(cleaned) if cleaned else 0.0
