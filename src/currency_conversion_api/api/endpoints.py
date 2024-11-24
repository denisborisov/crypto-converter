"""API endpoints group."""

import typing

import fastapi
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from .. import domain
from ..adapters import http_client
from ..views import currency_pairs
from ..settings import AppSettings


api_router = APIRouter()


@api_router.get("/convert", status_code=200, response_model=list[domain.schemata.ConversionGetResponse])
async def convert(
    request: typing.Annotated[domain.schemata.ConversionGetRequest, fastapi.Depends()],
    http_client: typing.Annotated[
        http_client.AbstractHttpClient, fastapi.Depends(http_client.HttpxClient),
    ],
) -> JSONResponse:
    conversion = domain.model.Conversion(
        amount=request.amount,
        base_currency=request.from_.strip().upper(),
        quote_currency=request.to.strip().upper(),
        desired_timestamp=request.desired_timestamp,
    )

    try:
        await currency_pairs.convert(conversion, http_client)
    except domain.exceptions.FetchCurrencyPairsError as ex:
        raise fastapi.HTTPException(
            detail=f"Error. Failed to get the currency pair due to unreachanble Quote Consumer endpoint. {ex.args[0]}",
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from ex
    except domain.exceptions.FetchCurrencyPairsNotFoundError as ex:
        raise fastapi.HTTPException(
            detail="Conversion is not possible. We don't have quotes for this pair.",
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
        ) from ex

    if conversion.conversion_rate_age_seconds > AppSettings.max_quote_age:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="quotes_outdated")

    return JSONResponse(
        content=jsonable_encoder(
            {
                "converted_amount": conversion.converted_amount,
                "conversion_rate": conversion.conversion_rate,
                "conversion_rate_age_seconds": conversion.conversion_rate_age_seconds,
                "actual_timestamp_closest_to_desired": conversion.actual_timestamp_closest_to_desired.strftime(
                    "%Y-%m-%dT%H:%M:%SZ",
                ),
            },
        ),
    )
