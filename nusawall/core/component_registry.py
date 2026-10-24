from __future__ import annotations

class ComponentRegistry:
    def __init__(self):
        self._items = {}

    def register(self, key: str, value: object) -> None:
        self._items[key] = value

    def get(self, key: str):
        return self._items[key]
