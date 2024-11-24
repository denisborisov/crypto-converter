# Runtime stage
FROM python:3.13-slim AS base-image

RUN apt-get update --yes \
    && apt-get upgrade --yes \
    && pip install --no-cache-dir --upgrade pip poetry \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf ~/.cache

FROM scratch AS runtime-image

ENV PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1

COPY --from=base-image / /

# Application stage
FROM base-image

ENV HOME_PATH="/home/crypto-converter"
ENV PATH=".venv/bin:${PATH}"
ENV EXCHANGE_API_URL="http://example.com"
ENV EXCHANGE_FETCH_INTERVAL=0
ENV QUOTE_CONSUMER_HOST=""
ENV QUOTE_CONSUMER_PORT=0
ENV DB_PORT=0
ENV CURRENCY_PAIR_TTL=0
ENV CURRENCY_CONVERSION_API_HOST=""
ENV CURRENCY_CONVERSION_API_PORT=0
ENV MAX_QUOTE_AGE=0
ENV QUOTE_CONSUMER_API_URL=""

WORKDIR ${HOME_PATH}

COPY ["src", "./src"]
COPY ["Dockerfile", \
    "poetry.lock", \
    "pyproject.toml", \
    "./"]

RUN poetry config virtualenvs.in-project true \
    && poetry install --only main \
    && groupadd --gid 1000 \
                crypto-converter \
    && useradd --uid 1000 \
                --gid crypto-converter \
                --home ${HOME_PATH} \
                --shell /bin/bash \
                crypto-converter \
    && chown --recursive \
                crypto-converter:crypto-converter \
                ./

USER crypto-converter

EXPOSE 8000 8001

ENTRYPOINT ["poetry", "run", "python", "-m", "src.run"]
