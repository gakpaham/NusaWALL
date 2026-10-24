from dataclasses import dataclass

@dataclass
class Equity:
    ticker: str
    exchange: str
    currency: str = "USD"
