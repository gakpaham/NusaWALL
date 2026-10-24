def normalize_ticker(value: str) -> str:
    return value.strip().upper().replace(".", "")
