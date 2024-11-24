"""Views related to currency pairs."""

import datetime

from ..adapters.currency_pair_repository import AbstractCurrencyPairRepository
from ..domain import model


async def fetch_currency_pair(
        symbol: str,
        timestamp: datetime.datetime | None,
        currency_pair_repo: AbstractCurrencyPairRepository,
) -> model.CurrencyPairBucket | None:
        return await currency_pair_repo.retrieve_latest_currency_pair(symbol, timestamp)
