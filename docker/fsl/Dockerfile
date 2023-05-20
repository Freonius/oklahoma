FROM --platform=linux/amd64 python:3.11-alpine

WORKDIR /app

COPY ./poetry.toml ./pyproject.toml ./

RUN echo 'no-pip = true' >> ./poetry.toml && \
    echo 'no-setuptools = true' >> ./poetry.toml && \
    pip install poetry && \
    poetry install --only main --no-root

FROM --platform=linux/amd64 python:3.11-alpine

WORKDIR /app

COPY . /app

RUN chmod +x ./entrypoint.sh && \
    echo '#!/usr/bin/env bash\n/app/entrypoint.sh start' > /bin/start && \
    echo '#!/usr/bin/env bash\n/app/entrypoint.sh start-dev' > /bin/start-dev && \
    chmod +x /bin/start && \
    chmod +x /bin/start-dev

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]

CMD start

COPY --from=stage /app/.venv /usr/.venv