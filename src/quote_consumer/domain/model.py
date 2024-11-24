"""Domain model."""

import datetime


class CurrencyPair:
    def __init__(
        self,
        *,
        symbol: str | None,
        conversion_rate: float | None,
    ) -> None:
        self.symbol = symbol
        self.conversion_rate = conversion_rate

    def __hash__(self) -> int:
        raise NotImplementedError


class CurrencyPairBucket:
    def __init__(
        self,
        *,
        currency_pairs: list[CurrencyPair],
        timestamp: datetime.datetime,
    ) -> None:
        self.currency_pairs = currency_pairs
        self.timestamp = timestamp

    def __hash__(self) -> int:
        raise NotImplementedError
