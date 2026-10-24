from dataclasses import dataclass

@dataclass
class BaseConfig:
    """Common config base class."""
    name: str = "nusawall"
