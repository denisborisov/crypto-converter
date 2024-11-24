"""Unit tests related to currency pairs view."""

import pytest

from . import conftest
from ..conftest import str_to_datetime
from src.currency_conversion_api import domain
from src.currency_conversion_api.views import currency_pairs


async def test_can_fetch_currency_pairs(fake_http_client: conftest.FakeHttpClient) -> None:
    conversion = domain.model.Conversion(
            amount=100,
            base_currency="RUB",
            quote_currency="USD",
            desired_timestamp=str_to_datetime("2025-05-01T00:00:00Z"),
        )

    result = await currency_pairs.fetch_currency_pairs(conversion, fake_http_client)

    assert result == {
        "conversion_rate": 500,
        "actual_timestamp_closest_to_desired": "2025-05-01T00:00:00Z",
    }


async def test_cannot_fetch_currency_pairs_if_unreachable(fake_http_client: conftest.FakeHttpClient) -> None:
    fake_http_client.raises_fetch_currency_pairs_error = True
    conversion = domain.model.Conversion(
            amount=100,
            base_currency="RUB",
            quote_currency="USD",
            desired_timestamp=str_to_datetime("2025-05-01T00:00:00Z"),
        )

    with pytest.raises(domain.exceptions.FetchCurrencyPairsError):
        await currency_pairs.fetch_currency_pairs(conversion, fake_http_client)
