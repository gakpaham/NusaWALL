from __future__ import annotations

class Exchange:
    code: str = "UNKNOWN"
    display_name: str = "Unknown exchange"

    def __init__(self, code: str | None = None):
        if code:
            self.code = code
