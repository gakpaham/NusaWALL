from datetime import datetime, timezone

class Clock:
    """Simple wall-clock abstraction for market-aware workflows."""
    @staticmethod
    def utcnow() -> datetime:
        return datetime.now(timezone.utc)
