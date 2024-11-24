"""Unit tests related to endpoints."""

import http

from fastapi.testclient import TestClient


class TestFetchCurrencyPair:
    async def test_can_convert(self, client: TestClient) -> None:
        fetch_responses = client.get("/api/convert?amount=100&from=rub&to=usd")

        assert fetch_responses.status_code == http.HTTPStatus.OK
        assert fetch_responses.json()["converted_amount"] == 50_000  # noqa: PLR2004
        assert fetch_responses.json()["conversion_rate"] == 500  # noqa: PLR2004
        assert fetch_responses.json()["conversion_rate_age_seconds"]
        assert fetch_responses.json()["actual_timestamp_closest_to_desired"] == "2025-05-01T00:00:00Z"

    async def test_cannot_convert_with_outdated_timestamp(self, client: TestClient) -> None:
        fetch_responses = client.get("/api/convert?amount=100&from=rub_with_outdated_timestamp&to=usd")

        assert fetch_responses.status_code == http.HTTPStatus.NOT_FOUND
        assert fetch_responses.json()["detail"] == "quotes_outdated"

    async def test_cannot_convert_with_invalid_timestamp(self, client: TestClient) -> None:
        fetch_responses = client.get("/api/convert?amount=100&from=rub&to=usd&desired_timestamp=abcdefg")

        assert fetch_responses.status_code == http.HTTPStatus.UNPROCESSABLE_CONTENT

    async def test_cannot_convert_if_unreachable(self, client_unreachable: TestClient) -> None:
        fetch_responses = client_unreachable.get("/api/convert?amount=100&from=rub&to=usd")

        assert fetch_responses.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert fetch_responses.json()["detail"].startswith(
            "Error. Failed to get the currency pair due to unreachanble Quote Consumer endpoint.",
        )

    async def test_cannot_convert_if_not_found(self, client_with_no_data: TestClient) -> None:
        fetch_responses = client_with_no_data.get("/api/convert?amount=100&from=rub&to=usd")

        assert fetch_responses.status_code == http.HTTPStatus.NOT_FOUND
        assert fetch_responses.json()["detail"] == "Conversion is not possible. We don't have quotes for this pair."
