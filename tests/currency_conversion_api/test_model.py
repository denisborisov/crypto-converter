"""Unit tests related to model."""

import datetime
import pytest

from .. import conftest
from src.currency_conversion_api.domain import model


class TestConversion:
    @pytest.mark.parametrize(
        ("amount", "base_currency", "quote_currency", "desired_timestamp"),
        [
            (100.1, "RUB", "USD", None),
            (100.1, "RUB", "USD", conftest.str_to_datetime("2025-05-01T00:00:00Z")),
        ],
    )
    def test_can_create_conversion(
        self,
        amount: float,
        base_currency: str,
        quote_currency: str,
        desired_timestamp: datetime.datetime,
    ) -> None:
        conversion = model.Conversion(
            amount=amount,
            base_currency=base_currency,
            quote_currency=quote_currency,
            desired_timestamp=desired_timestamp,
        )


        assert conversion.amount == amount
        assert conversion.base_currency == base_currency
        assert conversion.quote_currency == quote_currency
        assert conversion.desired_timestamp == desired_timestamp

    def test_cannot_hash_conversion(self) -> None:
        conversion = model.Conversion(
            amount=100,
            base_currency="RUB",
            quote_currency="USD",
            desired_timestamp=conftest.str_to_datetime("2025-05-01T00:00:00Z"),
        )

        with pytest.raises(NotImplementedError):
            hash(conversion)

    def test_calculate_conversion_amount_if_set_convertion_rate(self) -> None:
        conversion = model.Conversion(
            amount=100,
            base_currency="RUB",
            quote_currency="USD",
            desired_timestamp=conftest.str_to_datetime("2025-05-01T00:00:00Z"),
        )

        conversion.conversion_rate = 0.01

        assert conversion.conversion_rate == 0.01  # noqa: PLR2004
        assert conversion.converted_amount == 1

    def test_calculate_conversion_rate_age_seconds_if_set_actual_timestamp_closest_to_desired(self) -> None:
        conversion = model.Conversion(
            amount=100,
            base_currency="RUB",
            quote_currency="USD",
            desired_timestamp=conftest.str_to_datetime("2025-05-01T00:00:00Z"),
        )

        conversion.actual_timestamp_closest_to_desired = "2025-05-01T00:00:00Z"  # type: ignore[assignment]

        assert conversion.actual_timestamp_closest_to_desired == conftest.str_to_datetime("2025-05-01T00:00:00Z")
        assert conversion.conversion_rate_age_seconds
