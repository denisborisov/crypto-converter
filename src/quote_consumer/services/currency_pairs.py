"""Services related to currency pairs."""

import asyncio
import logging
from datetime import datetime, timezone

from ..adapters.currency_pair_repository import AbstractCurrencyPairRepository
from ..adapters.http_client import AbstractHttpClient
from ..domain import exceptions, model
from ..settings import AppSettings


async def load_currency_pairs(
        http_client: AbstractHttpClient,
        currency_pair_repo: AbstractCurrencyPairRepository,
) -> None:
    async with http_client:
        while True:
            if currency_pairs_json := await fetch_currency_pairs(http_client):
                currency_pair_bucket = create_currency_pair_bucket_from_json(currency_pairs_json)
                await save_currency_pair_bucket(currency_pair_bucket, currency_pair_repo)

            await asyncio.sleep(AppSettings.exchange_fetch_interval)


async def fetch_currency_pairs(http_client: AbstractHttpClient) -> list[dict] | None:
    logging.info(f"Trying to fetch currency pairs from {AppSettings.exchange_api_url.unicode_string()}.")
    try:
        response = await http_client.get(AppSettings.exchange_api_url.unicode_string())
    except (exceptions.HTTPBadRequestError, exceptions.HTTPBadResponseError) as ex:
        logging.exception(f"Failed to fetch currency pairs. {ex.args[0]}")
    else:
        logging.info("Currency pairs successfully fetched.")
        return list(response.json())
    return None


def create_currency_pair_bucket_from_json(currency_pairs_json: list[dict]) -> model.CurrencyPairBucket:
    currency_pairs = [
        model.CurrencyPair(symbol=one_currency_pair.get("symbol"), conversion_rate=one_currency_pair.get("price"))
        for one_currency_pair in currency_pairs_json
    ]
    return model.CurrencyPairBucket(
        currency_pairs=currency_pairs,
        timestamp=datetime.now(timezone.utc),
    )


async def save_currency_pair_bucket(
    currency_pair_bucket: model.CurrencyPairBucket,
    currency_pair_repo: AbstractCurrencyPairRepository,
) -> None:
    try:
        await currency_pair_repo.create_currency_pair_bucket(currency_pair_bucket=currency_pair_bucket)
    except Exception as ex:
        logging.exception(f"Failed to store currency pairs. {ex.args[0]}")
    else:
        logging.info(
            f"Currency pairs successfully stored with key: {
                currency_pair_bucket.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
            }",
        )
