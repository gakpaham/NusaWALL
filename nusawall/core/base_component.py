from dataclasses import dataclass

@dataclass
class BaseComponent:
    """Base component used across the system."""
    name: str = "component"
