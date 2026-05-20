FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /uvx /usr/local/bin/

WORKDIR /app

COPY pyproject.toml README.md uv.lock ./
COPY ainfera_mcp ./ainfera_mcp
RUN uv sync --frozen --no-dev

EXPOSE 8000

# Shell form so Railway-injected ${PORT} expands.
CMD .venv/bin/uvicorn ainfera_mcp.asgi:app --host 0.0.0.0 --port ${PORT:-8000}
