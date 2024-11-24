"""Schemata for CRUD operations."""

import datetime
import typing

import pydantic
from fastapi import Query


class ConversionGetRequest(pydantic.BaseModel):
    amount: float = pydantic.Field(Query(..., example="100", gt=0))
    from_: str = pydantic.Field(Query(..., alias="from", example="LTC"))
    to: str = pydantic.Field(Query(..., example="BTC"))
    desired_timestamp: datetime.datetime | None = pydantic.Field(Query(None, example="2024-11-24T12:00:00Z"))

    model_config: typing.ClassVar = {
        "json_schema_extra": {
            "examples": [
                {
                    "amount": "100",
                    "from": "LTC",
                    "to": "BTC",
                    "desired_timestamp": "2024-11-23T16:45:31Z",
                },
            ],
        },
    }


class ConversionGetResponse(pydantic.BaseModel):
    converted_amount: float
    conversion_rate: float
    conversion_rate_age_seconds: float
    actual_timestamp_closest_to_desired: str

    model_config: typing.ClassVar = {
        "json_schema_extra": {
            "examples": [
                {
                    "converted_amount": "0.00001012",
                    "conversion_rate": "0.00101200",
                    "conversion_rate_age_seconds": "15.0",
                    "actual_timestamp_closest_to_desired": "2024-11-23T16:45:31Z",
                },
            ],
        },
    }
