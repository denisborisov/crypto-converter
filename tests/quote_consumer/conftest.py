"""Quote Consumer fixtures."""

import datetime
import httpx
import pytest
import typing

from fastapi.testclient import TestClient

from .. import conftest
from src.quote_consumer.adapters import currency_pair_repository
from src.quote_consumer.adapters.http_client import AbstractHttpClient
from src.quote_consumer.domain import exceptions, model
from src.quote_consumer.main import app
from src.quote_consumer.settings import AppSettings


class FakeCurrencyPairRepository(currency_pair_repository.AbstractCurrencyPairRepository):
    def __init__(self) -> None:
        self.currency_pair_buckets: dict[str, dict[str | None, str | float]] = {}
        self.available_currency_pair_timestamps: list[dict[str, float]] = []
        self.raises_exception = False

    async def _create_currency_pairs(
        self,
        currency_pairs: list[model.CurrencyPair],
        timestamp: datetime.datetime,
    ) -> None:
        if self.raises_exception:
            raise exceptions.DBConnectionError("Error. No connection with DB.")
        for currency_pair in currency_pairs:
            self.currency_pair_buckets[
                timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
            ] = {currency_pair.symbol: str(currency_pair.conversion_rate)}

    async def _set_ttl(self, timestamp: datetime.datetime) -> None:
        self.currency_pair_buckets[timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")]["ttl"] = AppSettings.currency_pair_ttl

    async def _update_ordered_set_of_timestamps(self, timestamp: datetime.datetime) -> None:
        timestamp_str = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.available_currency_pair_timestamps.append(
            {
                timestamp_str: datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
                .replace(tzinfo=datetime.timezone.utc).timestamp(),
            },
        )

    async def _retrieve_currency_pair_bucket(self, timestamp: datetime.datetime) -> model.CurrencyPairBucket:
        currency_pairs: dict[str | None, str | float] = self.currency_pair_buckets[
            timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        ]
        return model.CurrencyPairBucket(
            currency_pairs=[
                model.CurrencyPair(symbol=symbol, conversion_rate=float(price))
                for symbol, price in currency_pairs.items()
            ],
            timestamp=timestamp,
        )

    async def _retrieve_latest_timestamp(self) -> datetime.datetime | None:
        latest_timestamp_str = next(iter(self.available_currency_pair_timestamps[-1]))
        return datetime.datetime.strptime(
            latest_timestamp_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc,
            )

    async def _retrieve_timestamp_range(self, start: float, end: float) -> list[datetime.datetime]:
        timestamps_items = [
            ts for ts in self.available_currency_pair_timestamps
            if start <= next(iter(ts.values())) and next(iter(ts.values())) <= end
        ]

        timestamps_str = [next(iter(ts.keys())) for ts in timestamps_items]
        return [
            datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
            for ts in timestamps_str
        ]


class FakeCurrencyPairRepositoryFilled(FakeCurrencyPairRepository):
    def __init__(self) -> None:
        self.available_currency_pair_timestamps = [
            {"2025-01-01T00:00:00Z": conftest.str_to_timestamp("2025-01-01T00:00:00Z")},
            {"2025-02-01T00:00:00Z": conftest.str_to_timestamp("2025-02-01T00:00:00Z")},
            {"2025-03-01T00:00:00Z": conftest.str_to_timestamp("2025-03-01T00:00:00Z")},
            {"2025-04-01T00:00:00Z": conftest.str_to_timestamp("2025-04-01T00:00:00Z")},
            {"2025-05-01T00:00:00Z": conftest.str_to_timestamp("2025-05-01T00:00:00Z")},
        ]
        self.currency_pair_buckets = {
            "2025-01-01T00:00:00Z": {"RUBUSD": 100},
            "2025-02-01T00:00:00Z": {"RUBUSD": 200},
            "2025-03-01T00:00:00Z": {"RUBUSD": 300},
            "2025-04-01T00:00:00Z": {"RUBUSD": 400},
            "2025-05-01T00:00:00Z": {"RUBUSD": 500},
        }


class FakeHttpClient(AbstractHttpClient):
    def __init__(self) -> None:
        self.raises_exception = False

    async def get(self, url: str) -> typing.Any:
        if self.raises_exception:
            raise exceptions.HTTPBadResponseError("Failed to make a get request")

        if url.startswith(AppSettings.exchange_api_url.unicode_string()):
            return httpx.Response(
                    status_code=200,
                    json={"status": "OK"},
                )

        raise httpx.HTTPStatusError(message=None, request=None, response=None)  # type: ignore[arg-type]


    class Response:
        def __init__(self, message: dict) -> None:
            self.message = message

        def json(self) -> dict:
            return self.message

    class FakeHttpClientError(Exception):
        pass


@pytest.fixture
def fake_currency_pair_repository() -> currency_pair_repository.AbstractCurrencyPairRepository:
    return FakeCurrencyPairRepository()


@pytest.fixture
def fake_http_client() -> AbstractHttpClient:
    return FakeHttpClient()


@pytest.fixture
def client() -> typing.Generator[TestClient, None, None]:
    app.dependency_overrides[currency_pair_repository.RedisCurrencyPairRepository] = FakeCurrencyPairRepositoryFilled
    yield TestClient(app)
    app.dependency_overrides.clear()
