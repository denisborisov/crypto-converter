"""Installation repository."""

import datetime
import typing

import fastapi
import redis.asyncio
import redis.exceptions

from ..domain import exceptions, model
from ..services import dependencies
from ..settings import AppSettings
# mypy: disable-error-code="misc"


class AbstractCurrencyPairRepository(typing.Protocol):
    async def create_currency_pair_bucket(self, currency_pair_bucket: model.CurrencyPairBucket) -> None:
        await self._create_currency_pairs(currency_pair_bucket.currency_pairs, currency_pair_bucket.timestamp)
        await self._set_ttl(currency_pair_bucket.timestamp)
        await self._update_ordered_set_of_timestamps(currency_pair_bucket.timestamp)

    async def _create_currency_pairs(
        self,
        currency_pairs: list[model.CurrencyPair],
        timestamp: datetime.datetime,
    ) -> None:
        raise NotImplementedError

    async def _set_ttl(self, timestamp: datetime.datetime) -> None:
        raise NotImplementedError

    async def _update_ordered_set_of_timestamps(self, timestamp: datetime.datetime) -> None:
        raise NotImplementedError

    async def retrieve_latest_currency_pair(
        self,
        symbol: str,
        desired_timestamp: datetime.datetime | None,
    ) -> model.CurrencyPairBucket | None:
        if not (retrieved_timestamp := await self._retrieve_relevant_timestamp(desired_timestamp)):
            return None
        currency_pair_bucket = await self._retrieve_currency_pair_bucket(retrieved_timestamp)

        if not (
            currency_pairs := [
                currency_pair for currency_pair in currency_pair_bucket.currency_pairs if currency_pair.symbol == symbol
            ]
        ):
            return None

        return model.CurrencyPairBucket(
            currency_pairs=[currency_pairs[0]],
            timestamp=retrieved_timestamp,
        )

    async def _retrieve_relevant_timestamp(
        self,
        desired_timestamp: datetime.datetime | None,
    ) -> datetime.datetime | None:
        if desired_timestamp:
            if not (
                actual_timestamp_closest_to_desired := await self._retrieve_timestamp_closest_to_desired(
                    desired_timestamp,
                )
            ):
                return None
            return actual_timestamp_closest_to_desired

        if not (latest_timestamp := await self._retrieve_latest_timestamp()):
            return None
        return latest_timestamp

    async def _retrieve_timestamp_closest_to_desired(
        self,
        desired_timestamp: datetime.datetime,
    ) -> datetime.datetime | None:
        start_of_day = datetime.datetime.combine(desired_timestamp.date(), datetime.datetime.min.time()).timestamp()
        end_of_day = datetime.datetime.combine(desired_timestamp.date(), datetime.datetime.max.time()).timestamp()

        if not (timestamps := await self._retrieve_timestamp_range(start_of_day, end_of_day)):
            return None

        return min(timestamps, key=lambda ts: abs(ts.timestamp() - desired_timestamp.timestamp()))

    async def _retrieve_currency_pair_bucket(self, timestamp: datetime.datetime) -> model.CurrencyPairBucket:
        raise NotImplementedError

    async def _retrieve_latest_timestamp(self) -> datetime.datetime | None:
        raise NotImplementedError

    async def _retrieve_timestamp_range(self, start: float, end: float) -> list[datetime.datetime]:
        raise NotImplementedError


class RedisCurrencyPairRepository(AbstractCurrencyPairRepository):
    def __init__(self, client: redis.asyncio.Redis = fastapi.Depends(dependencies.get_db_client)) -> None:
        self._client = client

    async def _create_currency_pairs(
        self,
        currency_pairs: list[model.CurrencyPair],
        timestamp: datetime.datetime,
    ) -> None:
        try:
            for currency_pair in currency_pairs:
                await self._client.hset(
                    timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    currency_pair.symbol,
                    str(currency_pair.conversion_rate),
                )
        except redis.exceptions.ConnectionError as ex:
            raise exceptions.DBConnectionError(
                f"Error. Failed to save all currency pairs in Redis for the {timestamp=}.",
            ) from ex

    async def _set_ttl(self, timestamp: datetime.datetime) -> None:
        try:
            await self._client.expire(timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"), AppSettings.currency_pair_ttl)
        except redis.exceptions.ConnectionError as ex:
            raise exceptions.DBConnectionError(f"Error. Failed to set the TTL for the {timestamp=}.") from ex

    async def _update_ordered_set_of_timestamps(self, timestamp: datetime.datetime) -> None:
        timestamp_str = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            await self._client.zadd(
                "available_currency_pair_timestamps",
                {
                    timestamp_str: datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
                    .replace(tzinfo=datetime.timezone.utc).timestamp(),
                },
            )
        except redis.exceptions.ConnectionError as ex:
            raise exceptions.DBConnectionError(
                f"Error. Failed to add the {timestamp=} to the 'available_currency_pair_timestamps' sorted set.",
            ) from ex

    async def _retrieve_currency_pair_bucket(self, timestamp: datetime.datetime) -> model.CurrencyPairBucket:
        try:
            currency_pairs: dict[str, str] = await self._client.hgetall(timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"))
        except redis.exceptions.ConnectionError as ex:
            raise exceptions.DBConnectionError(
                f"Error. Failed to retrieve currency pairs from Redis for the {timestamp=}.",
            ) from ex
        return model.CurrencyPairBucket(
            currency_pairs=[
                model.CurrencyPair(symbol=symbol, conversion_rate=float(conversion_rate))
                for symbol, conversion_rate in currency_pairs.items()
            ],
            timestamp=timestamp,
        )

    async def _retrieve_latest_timestamp(self) -> datetime.datetime | None:
        try:
            latest_timestamp_str = await self._client.zrange("available_currency_pair_timestamps", -1, -1)
        except redis.exceptions.ConnectionError as ex:
            raise exceptions.DBConnectionError("Error. Failed to retrieve the latest timestamp from Redis.") from ex
        return datetime.datetime.strptime(
            latest_timestamp_str[0], "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=datetime.timezone.utc,
            )

    async def _retrieve_timestamp_range(self, start: float, end: float) -> list[datetime.datetime]:
        try:
            timestamps_str = await self._client.zrangebyscore("available_currency_pair_timestamps", start, end)
        except redis.exceptions.ConnectionError as ex:
            raise exceptions.DBConnectionError(
                f"Error. Failed to retrieve timestamp range from {start} to {end} from Redis.",
            ) from ex
        return [
            datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
            for ts in timestamps_str
        ]
