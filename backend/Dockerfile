FROM python:3.10-slim

# system deps
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN mkdir -p /app/data
COPY pyproject.toml uv.lock /app/
RUN uv sync

COPY src/ /app/src/
COPY main.py /app/