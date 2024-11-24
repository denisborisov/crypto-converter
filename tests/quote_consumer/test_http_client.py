"""Unit tests related to HTTP client."""

import pytest

from pytest_httpx import HTTPXMock

from src.quote_consumer.domain import exceptions
from src.quote_consumer.adapters.http_client import HttpxClient


class TestHttpxClient:
    async def test_get_raises_if_request_error(self) -> None:
        async with HttpxClient() as client:
            with pytest.raises(exceptions.HTTPBadRequestError):
                await client.get(url="")

    async def test_get_raises_if_http_status_error(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(status_code=400)
        async with HttpxClient() as client:
            with pytest.raises(exceptions.HTTPBadResponseError):
                await client.get(url="https://test_url")
