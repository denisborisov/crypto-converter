"""Services related to database."""

import redis.asyncio

from ..adapters import http_client
from ..settings import AppSettings


def get_db_client() -> redis.asyncio.Redis:
    return redis.asyncio.Redis(host=AppSettings.db_host, port=AppSettings.db_port, decode_responses=True)


def get_http_client() -> http_client.AbstractHttpClient:
    return http_client.HttpxClient()
