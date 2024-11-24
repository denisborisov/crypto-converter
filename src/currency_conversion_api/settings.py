"""App configuration."""

import pydantic
from pydantic_settings import BaseSettings
# mypy: disable-error-code="call-overload"


class Settings(BaseSettings):
    max_quote_age: int = pydantic.Field(default="", env="MAX_QUOTE_AGE")
    quote_consumer_api_url: str = pydantic.Field(default="", env="QUOTE_CONSUMER_API_URL")

    # Related to Currency Conversion API
    currency_conversion_api_host: str = pydantic.Field(
        default="", env="CURRENCY_CONVERSION_API_HOST",
    )
    currency_conversion_api_port: int = pydantic.Field(
        default="", env="CURRENCY_CONVERSION_API_PORT",
    )

AppSettings = Settings()
