"""Unit tests related to currency pair repository."""

import datetime
import pytest

from . import conftest
from ..conftest import str_to_datetime, str_to_timestamp
from src.quote_consumer.domain import model
from src.quote_consumer.settings import AppSettings


class TestCreateCurrencyPairBucket:
    async def test_can_create_currency_pair_bucket(
        self,
        fake_currency_pair_repository: conftest.FakeCurrencyPairRepository,
    ) -> None:
        currency_pair_bucket = model.CurrencyPairBucket(
            currency_pairs=[model.CurrencyPair(symbol="RUBUSD", conversion_rate=100)],
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )

        await fake_currency_pair_repository.create_currency_pair_bucket(currency_pair_bucket)

        assert fake_currency_pair_repository.currency_pair_buckets == {
            currency_pair_bucket.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"): {
                "RUBUSD": "100",
                "ttl": AppSettings.currency_pair_ttl,
            },
        }

    @pytest.mark.parametrize(
        ("input_", "output"),
        [
            (
                {
                    "symbol": "RUBUSD",
                    "desired_timestamp": str_to_datetime("2025-01-01T00:00:00Z"),
                },
                {
                    "timestamp": str_to_datetime("2025-01-01T00:00:00Z"),
                    "symbol": "RUBUSD",
                    "conversion_rate": 100,
                },
            ),
            (
                {
                    "symbol": "RUBUSD",
                    "desired_timestamp": str_to_datetime("2025-01-31T00:00:00Z"),
                },
                None,
            ),
            (
                {
                    "symbol": "AAABBB",
                    "desired_timestamp": str_to_datetime("2025-01-31T00:00:00Z"),
                },
                None,
            ),
            (
                {
                    "symbol": "RUBUSD",
                    "desired_timestamp": None,
                },
                {
                    "timestamp": str_to_datetime("2025-05-01T00:00:00Z"),
                    "symbol": "RUBUSD",
                    "conversion_rate": 500,
                },
            ),
        ],
    )
    async def test_can_retrieve_latest_currency_pair(
        self,
        input_: dict,
        output: dict | None,
        fake_currency_pair_repository: conftest.FakeCurrencyPairRepository,
    ) -> None:
        fake_currency_pair_repository.available_currency_pair_timestamps = [
            {"2025-01-01T00:00:00Z": str_to_timestamp("2025-01-01T00:00:00Z")},
            {"2025-02-01T00:00:00Z": str_to_timestamp("2025-02-01T00:00:00Z")},
            {"2025-03-01T00:00:00Z": str_to_timestamp("2025-03-01T00:00:00Z")},
            {"2025-04-01T00:00:00Z": str_to_timestamp("2025-04-01T00:00:00Z")},
            {"2025-05-01T00:00:00Z": str_to_timestamp("2025-05-01T00:00:00Z")},
        ]
        fake_currency_pair_repository.currency_pair_buckets = {
            "2025-01-01T00:00:00Z": {"RUBUSD": 100},
            "2025-02-01T00:00:00Z": {"RUBUSD": 200},
            "2025-03-01T00:00:00Z": {"RUBUSD": 300},
            "2025-04-01T00:00:00Z": {"RUBUSD": 400},
            "2025-05-01T00:00:00Z": {"RUBUSD": 500},
        }

        result = await fake_currency_pair_repository.retrieve_latest_currency_pair(
            input_["symbol"],
            input_["desired_timestamp"],
        )

        if not result:
            assert not output
        else:
            assert output
            assert len(result.currency_pairs) == 1
            assert result.timestamp == output["timestamp"]
            assert result.currency_pairs[0].symbol == output["symbol"]
            assert result.currency_pairs[0].conversion_rate == output["conversion_rate"]

    @pytest.mark.parametrize(
        ("desired_timestamp", "resulted_timestamp"),
        [
            (str_to_datetime("2025-01-01T11:12:13Z"), str_to_datetime("2025-01-01T00:00:00Z")),
            (str_to_datetime("2025-01-31T00:00:00Z"), None),
            (None, str_to_datetime("2025-05-01T00:00:00Z")),
        ],
    )
    async def test_can_retrieve_relevant_timestamp(
        self,
        desired_timestamp: datetime.datetime | None,
        resulted_timestamp: datetime.datetime | None,
        fake_currency_pair_repository: conftest.FakeCurrencyPairRepository,
    ) -> None:
        fake_currency_pair_repository.available_currency_pair_timestamps = [
            {"2025-01-01T00:00:00Z": str_to_timestamp("2025-01-01T00:00:00Z")},
            {"2025-02-01T00:00:00Z": str_to_timestamp("2025-02-01T00:00:00Z")},
            {"2025-03-01T00:00:00Z": str_to_timestamp("2025-03-01T00:00:00Z")},
            {"2025-04-01T00:00:00Z": str_to_timestamp("2025-04-01T00:00:00Z")},
            {"2025-05-01T00:00:00Z": str_to_timestamp("2025-05-01T00:00:00Z")},
        ]

        result = await fake_currency_pair_repository._retrieve_relevant_timestamp(  # noqa: SLF001
            desired_timestamp=desired_timestamp,
        )

        assert result == resulted_timestamp


    @pytest.mark.parametrize(
        ("desired_timestamp", "resulted_timestamp"),
        [
            (str_to_datetime("2025-01-01T00:00:00Z"), str_to_datetime("2025-01-01T00:00:00Z")),
            (str_to_datetime("2025-02-01T00:00:00Z"), str_to_datetime("2025-02-01T00:00:00Z")),
            (str_to_datetime("2025-02-02T00:00:00Z"), None),
            (str_to_datetime("2025-03-01T12:12:12Z"), str_to_datetime("2025-03-01T00:00:00Z")),
        ],
    )
    async def test_can_retrieve_timestamp_closest_to_desired(
        self,
        desired_timestamp: datetime.datetime,
        resulted_timestamp: datetime.datetime | None,
        fake_currency_pair_repository: conftest.FakeCurrencyPairRepository,
    ) -> None:
        fake_currency_pair_repository.available_currency_pair_timestamps = [
            {"2025-01-01T00:00:00Z": str_to_timestamp("2025-01-01T00:00:00Z")},
            {"2025-02-01T00:00:00Z": str_to_timestamp("2025-02-01T00:00:00Z")},
            {"2025-03-01T00:00:00Z": str_to_timestamp("2025-03-01T00:00:00Z")},
            {"2025-04-01T00:00:00Z": str_to_timestamp("2025-04-01T00:00:00Z")},
            {"2025-05-01T00:00:00Z": str_to_timestamp("2025-05-01T00:00:00Z")},
        ]

        result = await fake_currency_pair_repository._retrieve_timestamp_closest_to_desired(  # noqa: SLF001
            desired_timestamp=desired_timestamp,
        )

        assert result == resulted_timestamp
