"""Services related to database."""

from functools import lru_cache

import redis.asyncio

from ..adapters import http_client
from ..settings import AppSettings


@lru_cache
def get_db_client() -> redis.asyncio.Redis:
    return redis.asyncio.Redis(host=AppSettings.db_host, port=AppSettings.db_port, decode_responses=True)


@lru_cache
def get_http_client() -> http_client.AbstractHttpClient:
    return http_client.HttpxClient()
