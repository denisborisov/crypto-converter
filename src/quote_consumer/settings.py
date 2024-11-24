"""App configuration."""

import pydantic
from pydantic_settings import BaseSettings
# mypy: disable-error-code="call-overload"


class Settings(BaseSettings):
    # Related to DB
    db_host: str = pydantic.Field(default="", env="DB_HOST")
    db_port: int = pydantic.Field(default="", env="DB_PORT")
    currency_pair_ttl: int = pydantic.Field(default=0, env="CURRENCY_PAIR_TTL")

    # Related to Exchange
    exchange_api_url: pydantic.HttpUrl = pydantic.Field(default="http://example.com", env="EXCHANGE_API_URL")
    exchange_fetch_interval: int = pydantic.Field(default=0, env="EXCHANGE_FETCH_INTERVAL")

    # Related to Quote Consumer
    quote_consumer_host: str = pydantic.Field(default="", env="QUOTE_CONSUMER_HOST")
    quote_consumer_port: int = pydantic.Field(default="", env="QUOTE_CONSUMER_PORT")


AppSettings = Settings()
