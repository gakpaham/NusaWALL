from __future__ import annotations

REGISTRY = {}

def register(name: str, obj: object) -> None:
    REGISTRY[name] = obj
