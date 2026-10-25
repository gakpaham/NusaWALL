from __future__ import annotations

from collections.abc import Callable
from time import sleep
from typing import TypeVar

T = TypeVar("T")


def retry(func: Callable[[], T], retries: int = 3, delay: float = 0.1) -> T:
    """Run a callable, retrying failures up to ``retries`` additional times."""
    if retries < 0:
        raise ValueError("retries must be non-negative")
    if delay < 0:
        raise ValueError("delay must be non-negative")

    for attempt in range(retries + 1):
        try:
            return func()
        except Exception:
            if attempt == retries:
                raise
            if delay:
                sleep(delay)

    raise RuntimeError("Retry loop exited unexpectedly")
