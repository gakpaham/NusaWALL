from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class RawRecord:
    source: str
    payload: dict
    event_time: datetime | None = None
    publish_time: datetime | None = None
    ingest_time: datetime | None = field(default_factory=datetime.utcnow)
