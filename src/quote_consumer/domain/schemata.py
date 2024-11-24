"""Schemata for CRUD operations."""

import datetime
import typing

import pydantic
from fastapi import Query


class CurrencyPairGetRequest(pydantic.BaseModel):
    base_currency: str = pydantic.Field(Query(...))
    quote_currency: str = pydantic.Field(Query(...))
    desired_timestamp: datetime.datetime | None = None

    model_config: typing.ClassVar = {
        "json_schema_extra": {
            "examples": [
                {
                    "base_currency": "LTC",
                    "quote_currency": "BTC",
                    "desired_timestamp": "2024-11-23T16:45:31Z",
                },
            ],
        },
    }


class CurrencyPairGetResponse(pydantic.BaseModel):
    conversion_rate: float
    actual_timestamp_closest_to_desired: str

    model_config: typing.ClassVar = {
        "json_schema_extra": {
            "examples": [
                {
                    "conversion_rate": "0.00101200",
                    "actual_timestamp_closest_to_desired": "2024-11-23T16:45:31Z",
                },
            ],
        },
    }
