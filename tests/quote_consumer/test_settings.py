"""Unit tests related to environment variables."""

import os

from src.quote_consumer.settings import AppSettings


class TestEnvironmentVariables:
    def test_environment_variables_exist(self) -> None:
        # Related to DB
        assert os.environ.get("DB_PORT")
        assert os.environ.get("CURRENCY_PAIR_TTL")

        # Related to Exchange
        assert os.environ.get("EXCHANGE_API_URL")
        assert os.environ.get("EXCHANGE_FETCH_INTERVAL")

        # Related to Quote Consumer
        assert os.environ.get("QUOTE_CONSUMER_HOST")
        assert os.environ.get("QUOTE_CONSUMER_PORT")


class TestSettings:
    def test_app_settings_initialized(self) -> None:
        # Related to DB
        assert AppSettings.db_port
        assert AppSettings.currency_pair_ttl

        # Related to Exchange
        assert AppSettings.exchange_api_url
        assert AppSettings.exchange_fetch_interval

        # Related to Quote Consumer
        assert AppSettings.quote_consumer_host
        assert AppSettings.quote_consumer_port
