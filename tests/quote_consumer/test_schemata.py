"""Unit tests related to schemata."""

from src.quote_consumer.domain import schemata


class TestCurrencyPairGetRequest:
    def test_currency_pair_get_request_contans_valid_config(self) -> None:
        example = schemata.CurrencyPairGetRequest.model_config["json_schema_extra"]["examples"][0]

        assert example["base_currency"] == "LTC"
        assert example["quote_currency"] == "BTC"
        assert example["desired_timestamp"] == "2024-11-23T16:45:31Z"


class TestCurrencyPairGetResponse:
    def test_currency_pair_get_response_contans_valid_config(self) -> None:
        example = schemata.CurrencyPairGetResponse.model_config["json_schema_extra"]["examples"][0]

        assert example["conversion_rate"] == "0.00101200"
        assert example["actual_timestamp_closest_to_desired"] == "2024-11-23T16:45:31Z"
