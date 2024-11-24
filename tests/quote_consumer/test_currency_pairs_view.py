"""Unit tests related to currency pairs view."""

import pytest

from . import conftest
from ..conftest import str_to_datetime, str_to_timestamp
from src.quote_consumer.views import currency_pairs


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

    result = await currency_pairs.fetch_currency_pair(
        input_["symbol"],
        input_["desired_timestamp"],
        fake_currency_pair_repository,
    )

    if not result:
        assert not output
    else:
        assert output
        assert len(result.currency_pairs) == 1
        assert result.timestamp == output["timestamp"]
        assert result.currency_pairs[0].symbol == output["symbol"]
        assert result.currency_pairs[0].conversion_rate == output["conversion_rate"]
