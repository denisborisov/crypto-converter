"""Crypto Converter app."""

import logging
import sys

from . import currency_conversion_api
from . import quote_consumer

if __name__ == "__main__":
    if len(sys.argv) < 2:  # noqa: PLR2004
        logging.log(logging.ERROR, "Usage: python run.py [api|quote-consumer]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "api":
        currency_conversion_api.main.run()
    elif command == "quote-consumer":
        quote_consumer.main.run()
    else:
        logging.log(logging.ERROR, f"Unknown command: {command}")
        sys.exit(1)
