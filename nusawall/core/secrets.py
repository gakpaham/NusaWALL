import os

def get_secret(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)
