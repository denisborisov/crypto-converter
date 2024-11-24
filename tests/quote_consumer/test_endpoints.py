"""Unit tests related to endpoints."""

import http

from fastapi.testclient import TestClient


class TestFetchCurrencyPair:
    async def test_can_fetch_currency_pair(self, client: TestClient) -> None:
        fetch_responses = client.get("/api/currency-pair?base_currency=rub&quote_currency=usd")

        assert fetch_responses.status_code == http.HTTPStatus.OK
        assert fetch_responses.json() == {
            "conversion_rate": 500,
            "actual_timestamp_closest_to_desired": "2025-05-01T00:00:00Z",
        }

    async def test_can_fetch_currency_pair_with_timestamp(self, client: TestClient) -> None:
        fetch_responses = client.get(
            "/api/currency-pair?base_currency=rub&quote_currency=usd&desired_timestamp=2025-02-01T11:12:13Z",
        )

        assert fetch_responses.status_code == http.HTTPStatus.OK
        assert fetch_responses.json() == {
            "conversion_rate": 200,
            "actual_timestamp_closest_to_desired": "2025-02-01T00:00:00Z",
        }

    async def test_cannot_fetch_currency_pair_with_invalid_currencies(self, client: TestClient) -> None:
        fetch_responses = client.get("/api/currency-pair?base_currency=aaa&quote_currency=bbb")

        assert fetch_responses.status_code == http.HTTPStatus.NOT_FOUND
        assert fetch_responses.json() == "Conversion is not possible. We don't have quotes for this pair."

    async def test_cannot_fetch_currency_pair_with_invalid_timestamp(self, client: TestClient) -> None:
        fetch_responses = client.get(
            "/api/currency-pair?base_currency=rub&quote_currency=usd&desired_timestamp=abcdefg",
        )

        assert fetch_responses.status_code == http.HTTPStatus.UNPROCESSABLE_CONTENT
