"""Exceptions."""

class HTTPBadRequestError(Exception):
    pass


class HTTPBadResponseError(Exception):
    pass


class FetchCurrencyPairsError(Exception):
    pass


class FetchCurrencyPairsNotFoundError(Exception):
    pass
