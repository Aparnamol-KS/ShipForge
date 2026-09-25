FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y git docker.io \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

WORKDIR /workspace