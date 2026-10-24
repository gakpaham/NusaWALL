from __future__ import annotations

def idx_tick_size(symbol: str) -> float:
    return 25.0 if symbol.endswith(".JK") else 0.01
