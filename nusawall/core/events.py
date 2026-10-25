from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class Event:
    name: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict | None = None
