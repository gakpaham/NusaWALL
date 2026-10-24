from dataclasses import dataclass

@dataclass
class RuleVersion:
    name: str
    effective_from: str
    effective_to: str | None = None
