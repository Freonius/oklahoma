FROM python:3.13.0a3-alpine AS stage

ENV PYTHONBUFFERED=1 \
    TZ=Europe/Rome \
    LOG_LEVEL=INFO

WORKDIR /app

COPY ./pyproject.toml ./poetry.toml ./poetry.lock /app/

RUN pip install poetry && \
    poetry install --only main --no-root

FROM python:3.13.0a3-alpine AS build

ENV PYTHONBUFFERED=1 \
    TZ=Europe/Rome \
    LOG_LEVEL=INFO

WORKDIR /app

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --from=stage /app/.venv/ ${VIRTUAL_ENV}

COPY . .
