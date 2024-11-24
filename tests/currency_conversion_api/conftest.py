"""Quote Consumer fixtures."""

import httpx
import pytest
import typing

from fastapi.testclient import TestClient

from src.currency_conversion_api.adapters import http_client
from src.currency_conversion_api.domain import exceptions
from src.currency_conversion_api.main import app
from src.currency_conversion_api.settings import AppSettings


class FakeHttpClient(http_client.AbstractHttpClient):
    def __init__(
        self,
        raises_fetch_currency_pairs_error: bool = False,
        raises_fetch_currency_pairs_not_found_error: bool = False,
    ) -> None:
        self.raises_fetch_currency_pairs_error = raises_fetch_currency_pairs_error
        self.raises_fetch_currency_pairs_not_found_error = raises_fetch_currency_pairs_not_found_error

    async def get(self, url: str, params: dict) -> typing.Any:
        if self.raises_fetch_currency_pairs_error:
            raise exceptions.HTTPBadResponseError("Failed to make a get request")
        if self.raises_fetch_currency_pairs_not_found_error:
            raise exceptions.FetchCurrencyPairsNotFoundError("Currency Pair Not Found.")

        if url.startswith(AppSettings.quote_consumer_api_url):
            if params["base_currency"] == "RUB_with_outdated_timestamp".upper():
                return httpx.Response(
                        status_code=200,
                        json={
                            "conversion_rate": 100,
                            "actual_timestamp_closest_to_desired": "2020-05-01T00:00:00Z",
                        },
                    )
            return httpx.Response(
                    status_code=200,
                    json={
                        "conversion_rate": 500,
                        "actual_timestamp_closest_to_desired": "2025-05-01T00:00:00Z",
                    },
                )

        raise httpx.HTTPStatusError(message=None, request=None, response=None)  # type: ignore[arg-type]


    class Response:
        def __init__(self, message: dict) -> None:
            self.message = message

        def json(self) -> dict:
            return self.message

    class FakeHttpClientError(Exception):
        pass


class FakeHttpClientUnreachable(FakeHttpClient):
    def __init__(self) -> None:
        FakeHttpClient.__init__(self, raises_fetch_currency_pairs_error=True)


class FakeHttpClientWithNoData(FakeHttpClient):
    def __init__(self) -> None:
        FakeHttpClient.__init__(self, raises_fetch_currency_pairs_not_found_error=True)


@pytest.fixture
def fake_http_client() -> http_client.AbstractHttpClient:
    return FakeHttpClient()


@pytest.fixture
def client() -> typing.Generator[TestClient, None, None]:
    app.dependency_overrides[http_client.HttpxClient] = FakeHttpClient
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def client_unreachable() -> typing.Generator[TestClient, None, None]:
    app.dependency_overrides[http_client.HttpxClient] = FakeHttpClientUnreachable
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def client_with_no_data() -> typing.Generator[TestClient, None, None]:
    app.dependency_overrides[http_client.HttpxClient] = FakeHttpClientWithNoData
    yield TestClient(app)
    app.dependency_overrides.clear()
