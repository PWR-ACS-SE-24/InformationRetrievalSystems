FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt update && apt-get --no-install-recommends install -y curl

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

ADD . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD [ "curl", "--fail", "http://localhost:2137/api/health" ]

CMD ["uv", "run", "uvicorn", "arxivsearch:app", "--host", "0.0.0.0", "--port", "2137", "--log-config", "/app/arxivsearch/logging.json", "--log-level", "info"]