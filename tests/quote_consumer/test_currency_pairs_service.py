"""Unit tests related to currency pairs service."""

import datetime
import logging
import pytest

from . import conftest
from ..conftest import str_to_datetime
from src.quote_consumer.domain import model
from src.quote_consumer.services import currency_pairs
from src.quote_consumer.settings import AppSettings


class TestFetchCurrencyPairBucket:
    async def test_can_fetch_currency_pair_bucket(
        self,
        fake_http_client: conftest.FakeHttpClient,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        with caplog.at_level(logging.INFO):
            await currency_pairs.fetch_currency_pairs(fake_http_client)

        assert f"Trying to fetch currency pairs from {AppSettings.exchange_api_url.unicode_string()}." in caplog.text
        assert "Currency pairs successfully fetched." in caplog.text

    async def test_cannot_fetch_currency_pair_bucket_if_eception(
        self,
        fake_http_client: conftest.FakeHttpClient,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        fake_http_client.raises_exception = True
        with caplog.at_level(logging.INFO):
            await currency_pairs.fetch_currency_pairs(fake_http_client)

        assert f"Trying to fetch currency pairs from {AppSettings.exchange_api_url.unicode_string()}." in caplog.text
        assert "Failed to fetch currency pairs." in caplog.text


class TestCreateCurrencyBucketFromJSON:
    async def test_can_create_currency_pair_bucket_from_json(
        self,
    ) -> None:
        currency_pairs_json = [{"symbol": "RUBUSD", "price": 100},{"symbol": "USDRUB", "price": 200}]

        currency_pair_bucket = currency_pairs.create_currency_pair_bucket_from_json(currency_pairs_json)

        assert len(currency_pair_bucket.currency_pairs) == 2  # noqa: PLR2004
        assert currency_pair_bucket.currency_pairs[0].symbol == currency_pairs_json[0]["symbol"]
        assert currency_pair_bucket.currency_pairs[0].conversion_rate == currency_pairs_json[0]["price"]
        assert currency_pair_bucket.currency_pairs[1].symbol == currency_pairs_json[1]["symbol"]
        assert currency_pair_bucket.currency_pairs[1].conversion_rate == currency_pairs_json[1]["price"]
        assert isinstance(currency_pair_bucket.timestamp, datetime.datetime)



class TestSaveCurrencyPairBucket:
    async def test_can_save_currency_pair_bucket(
        self,
        fake_currency_pair_repository: conftest.FakeCurrencyPairRepository,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        currency_pair_bucket = model.CurrencyPairBucket(
            currency_pairs=[model.CurrencyPair(symbol="RUBUSD", conversion_rate=100)],
            timestamp=str_to_datetime("2025-01-01T00:00:00Z"),
        )

        with caplog.at_level(logging.INFO):
            await currency_pairs.save_currency_pair_bucket(
                currency_pair_bucket,
                fake_currency_pair_repository,
            )

        assert f"Currency pairs successfully stored with key: {
            currency_pair_bucket.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        }" in caplog.text

    async def test_cannot_save_currency_pair_bucket_if_exception(
        self,
        fake_currency_pair_repository: conftest.FakeCurrencyPairRepository,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        fake_currency_pair_repository.raises_exception = True
        currency_pair_bucket = model.CurrencyPairBucket(
            currency_pairs=[model.CurrencyPair(symbol="RUBUSD", conversion_rate=100)],
            timestamp=str_to_datetime("2025-01-01T00:00:00Z"),
        )

        with caplog.at_level(logging.INFO):
            await currency_pairs.save_currency_pair_bucket(
                currency_pair_bucket,
                fake_currency_pair_repository,
            )

        assert "Failed to store currency pairs." in caplog.text
