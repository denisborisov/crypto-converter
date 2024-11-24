"""Unit tests related to environment variables."""

import os

from src.currency_conversion_api.settings import AppSettings


class TestEnvironmentVariables:
    def test_environment_variables_exist(self) -> None:
        assert os.environ.get("MAX_QUOTE_AGE")
        assert os.environ.get("QUOTE_CONSUMER_API_URL")

        # Related to Currency Conversion API
        assert os.environ.get("CURRENCY_CONVERSION_API_HOST")
        assert os.environ.get("CURRENCY_CONVERSION_API_PORT")


class TestSettings:
    def test_app_settings_initialized(self) -> None:
        assert AppSettings.max_quote_age
        assert AppSettings.quote_consumer_api_url

        # Related to Currency Conversion API
        assert AppSettings.currency_conversion_api_host
        assert AppSettings.currency_conversion_api_port
