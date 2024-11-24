"""Schemata for CRUD operations."""

import datetime
import typing

import pydantic
from fastapi import Query


class CurrencyPairGetRequest(pydantic.BaseModel):
    base_currency: str = pydantic.Field(Query(..., example="LTC"))
    quote_currency: str = pydantic.Field(Query(..., example="BTC"))
    desired_timestamp: datetime.datetime | None = pydantic.Field(Query(None, example="2024-11-24T12:00:00Z"))

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
