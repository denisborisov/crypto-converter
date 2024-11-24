"""Domain model."""

import datetime


class Conversion:
    def __init__(
        self,
        *,
        amount: float,
        base_currency: str,
        quote_currency: str,
        desired_timestamp: datetime.datetime | None,
    ) -> None:
        self.amount = amount
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.desired_timestamp = desired_timestamp
        self._converted_amount: float
        self._conversion_rate: float
        self._conversion_rate_age_seconds: float
        self._actual_timestamp_closest_to_desired: datetime.datetime

    @property
    def converted_amount(self) -> float:
        return self._converted_amount

    @property
    def conversion_rate(self) -> float:
        return self._conversion_rate

    @conversion_rate.setter
    def conversion_rate(self, value: float) -> None:
        self._conversion_rate = value
        self._converted_amount = self.amount * self._conversion_rate

    @property
    def conversion_rate_age_seconds(self) -> float:
        return self._conversion_rate_age_seconds

    @property
    def actual_timestamp_closest_to_desired(self) -> datetime.datetime:
        return self._actual_timestamp_closest_to_desired

    @actual_timestamp_closest_to_desired.setter
    def actual_timestamp_closest_to_desired(self, value: str) -> None:
        self._actual_timestamp_closest_to_desired = datetime.datetime.strptime(
            value, "%Y-%m-%dT%H:%M:%SZ",
        ).replace(tzinfo=datetime.timezone.utc)
        current_time = datetime.datetime.now(datetime.timezone.utc)
        self._conversion_rate_age_seconds = (current_time - self._actual_timestamp_closest_to_desired).total_seconds()

    def __hash__(self) -> int:
        raise NotImplementedError
