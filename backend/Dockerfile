FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y git docker.io \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN pip install uv

RUN uv sync --frozen --no-dev

COPY app ./app

CMD ["/app/.venv/bin/python", "-c", "from app.redis_client.worker import run_worker; run_worker()"]