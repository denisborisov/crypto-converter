"""Unit tests related to schemata."""

from src.currency_conversion_api.domain import schemata


class TestConversionGetRequest:
    def test_conversion_get_request_contans_valid_config(self) -> None:
        example = schemata.ConversionGetRequest.model_config["json_schema_extra"]["examples"][0]

        assert example["amount"] == "100"
        assert example["from"] == "LTC"
        assert example["to"] == "BTC"
        assert example["desired_timestamp"] == "2024-11-23T16:45:31Z"


class TestConversionGetResponse:
    def test_conversion_get_response_contans_valid_config(self) -> None:
        example = schemata.ConversionGetResponse.model_config["json_schema_extra"]["examples"][0]

        assert example["converted_amount"] == "0.00001012"
        assert example["conversion_rate"] == "0.00101200"
        assert example["conversion_rate_age_seconds"] == "15.0"
        assert example["actual_timestamp_closest_to_desired"] == "2024-11-23T16:45:31Z"
