"""Views related to currency pairs."""

from ..adapters.http_client import AbstractHttpClient
from ..domain import exceptions, model

from ..settings import AppSettings


async def convert(conversion: model.Conversion, http_client: AbstractHttpClient) -> None:
        currency_pairs = await fetch_currency_pairs(conversion, http_client)
        conversion.conversion_rate = currency_pairs["conversion_rate"]
        conversion.actual_timestamp_closest_to_desired = currency_pairs["actual_timestamp_closest_to_desired"]


async def fetch_currency_pairs(conversion: model.Conversion, http_client: AbstractHttpClient) -> dict:
        params: dict = {"base_currency": conversion.base_currency, "quote_currency": conversion.quote_currency}
        if conversion.desired_timestamp:
                params.update({"desired_timestamp": conversion.desired_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")})
        try:
                response = await http_client.get(
                        f"{AppSettings.quote_consumer_api_url}/api/currency-pair",
                        params=params,
                )
        except (exceptions.HTTPBadRequestError, exceptions.HTTPBadResponseError) as ex:
                if "404 Not Found" in ex.args[0]:
                        raise exceptions.FetchCurrencyPairsNotFoundError from ex
                raise exceptions.FetchCurrencyPairsError(f"Failed to fetch currency pairs. {ex.args[0]}") from ex
        return dict(response.json())
