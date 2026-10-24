from __future__ import annotations

from .base import BaseConfig


def apply_overrides(config: BaseConfig, overrides: dict | None = None) -> BaseConfig:
    if overrides:
        for key, value in overrides.items():
            setattr(config, key, value)
    return config
