"""API endpoints group."""

from typing import Annotated

import fastapi
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .. import domain
from ..views import currency_pairs
from ..adapters import currency_pair_repository


api_router = APIRouter()


@api_router.get("/currency-pair", status_code=200, response_model=list[domain.schemata.CurrencyPairGetResponse])
async def get_currency_pair(
    request: Annotated[domain.schemata.CurrencyPairGetRequest, fastapi.Depends()],
    currency_pair_repo: Annotated[
        currency_pair_repository.AbstractCurrencyPairRepository,
        fastapi.Depends(currency_pair_repository.RedisCurrencyPairRepository),
    ],
) -> JSONResponse:
    try:
        if result := await currency_pairs.fetch_currency_pair(
            symbol = f"{request.base_currency.strip()}{request.quote_currency.strip()}".upper(),
            timestamp=request.desired_timestamp,
            currency_pair_repo=currency_pair_repo,
        ):
            return JSONResponse(
                content={
                    "conversion_rate": result.currency_pairs[0].conversion_rate,
                    "actual_timestamp_closest_to_desired": result.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
            )
    except domain.exceptions.DBConnectionError as ex:
        raise fastapi.HTTPException(
            detail=f"Error. Failed to get the currency pair due to unreachanble database. {ex.args[0]}",
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from ex

    return JSONResponse(
        content="Conversion is not possible. We don't have quotes for this pair.",
        status_code=fastapi.status.HTTP_404_NOT_FOUND,
    )
