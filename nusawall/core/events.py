from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Event:
    name: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    payload: dict | None = None
