from __future__ import annotations

from time import sleep


def retry(func, retries: int = 3, delay: float = 0.1):
    for _ in range(retries):
        try:
            return func()
        except Exception:
            sleep(delay)
    return func()
