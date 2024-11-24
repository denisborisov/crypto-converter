"""General fixtures."""

import datetime


def str_to_datetime(timestamp_str: str) -> datetime.datetime:
    return datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)


def str_to_timestamp(timestamp_str: str) -> float:
    return str_to_datetime(timestamp_str).timestamp()
