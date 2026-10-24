from functools import lru_cache

@lru_cache(maxsize=128)
def memoized_identity(value: str) -> str:
    return value
