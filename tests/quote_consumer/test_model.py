"""Unit tests related to model."""

import datetime
import pytest

from src.quote_consumer.domain import model


class TestCurrencyPair:
    @pytest.mark.parametrize(
        ("symbol", "conversion_rate"),
        [
            ("RUBUSD", 100.1),
            (None, None),
        ],
    )
    def test_can_create_currency_pair(self, symbol: str, conversion_rate: float) -> None:
        currency_pair = model.CurrencyPair(symbol=symbol, conversion_rate=conversion_rate)

        assert currency_pair.symbol == symbol
        assert currency_pair.conversion_rate == conversion_rate

    def test_cannot_hash_currency_pair(self) -> None:
        currency_pair = model.CurrencyPair(symbol="RUB", conversion_rate=100.1)

        with pytest.raises(NotImplementedError):
            hash(currency_pair)

class TestCurrencyPairBucket:
    def test_can_create_currency_pair_bucket(self) -> None:
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        currency_pair = model.CurrencyPair(symbol="RUB", conversion_rate=100.1)
        currency_pair_bucket = model.CurrencyPairBucket(
            currency_pairs=[currency_pair],
            timestamp=timestamp,
        )

        assert currency_pair_bucket.currency_pairs == [currency_pair]
        assert currency_pair_bucket.timestamp == timestamp

    def test_cannot_hash_currency_pair_bucket(self) -> None:
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        currency_pair = model.CurrencyPair(symbol="RUB", conversion_rate=100.1)
        currency_pair_bucket = model.CurrencyPairBucket(
            currency_pairs=[currency_pair],
            timestamp=timestamp,
        )

        with pytest.raises(NotImplementedError):
            hash(currency_pair_bucket)
