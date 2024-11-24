"""App entrypoint."""

import asyncio

import fastapi
from uvicorn import Config, Server

from .adapters import currency_pair_repository
from .api import endpoints
from .services import currency_pairs, dependencies
from .settings import AppSettings


app = fastapi.FastAPI(
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    title="Quote Consumer",
    description="This app fetches data from Exchange and stores it.",
    version="1.0.0",
    contact={
        "url": "https://github.com/denisborisov",
        "name": "Denis Borisov",
        "email": "denis.borisov@hotmail.com",
    },
)


app.include_router(endpoints.api_router, prefix="/api")


async def main() -> None:
    server = Server(Config(app=app, host=AppSettings.quote_consumer_host, port=AppSettings.quote_consumer_port))
    tasks = [
        asyncio.create_task(server.serve()),
        asyncio.create_task(
            currency_pairs.load_currency_pairs(
                http_client=dependencies.get_http_client(),
                currency_pair_repo=currency_pair_repository.RedisCurrencyPairRepository(dependencies.get_db_client()),
            ),
        ),
    ]

    await asyncio.gather(*tasks)


def run() -> None:
    asyncio.run(main())
