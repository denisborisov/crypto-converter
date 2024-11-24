"""App entrypoint."""

import fastapi
import uvicorn

from .api import endpoints
from .settings import AppSettings


app = fastapi.FastAPI(
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    title="Currency Conversion API",
    description="This app converts money using Quote Consumer API.",
    version="1.0.0",
    contact={
        "url": "https://github.com/denisborisov",
        "name": "Denis Borisov",
        "email": "denis.borisov@hotmail.com",
    },
)


app.include_router(endpoints.api_router, prefix="/api")


def run() -> None:
    uvicorn.run(app, host=AppSettings.currency_conversion_api_host, port=AppSettings.currency_conversion_api_port)
