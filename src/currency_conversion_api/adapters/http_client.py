"""Class to fetch data from controllers."""

import types
import typing
import typing_extensions

import httpx

from ..domain import exceptions


class AbstractHttpClient(typing.Protocol):
    async def __aenter__(self) -> typing_extensions.Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> bool | None:
        return None

    async def get(self, url: str, params: dict) -> typing.Any:
        pass


class HttpxClient(AbstractHttpClient):
    def __init__(self) -> None:
        self.client = httpx.AsyncClient()

    async def __aenter__(self) -> typing_extensions.Self:
        await super().__aenter__()
        self.client = await self.client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> bool | None:
        await super().__aexit__(exc_type, exc_val, exc_tb)
        await self.client.__aexit__(exc_type, exc_val, exc_tb)
        return None

    async def get(self, url: str, params: dict) -> httpx.Response:
        try:
            response = await self.client.get(url, params=params)
        except httpx.RequestError as ex:
            raise exceptions.HTTPBadRequestError(ex.args[0]) from ex
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as ex:
            raise exceptions.HTTPBadResponseError(ex.args[0]) from ex
        return response
