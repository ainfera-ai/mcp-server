FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /uvx /usr/local/bin/

WORKDIR /app

COPY pyproject.toml README.md uv.lock ./
COPY ainfera_mcp ./ainfera_mcp
RUN uv sync --frozen --no-dev

ENV AINFERA_MCP_TRANSPORT=http

EXPOSE 8000

# Shell form so Railway-injected ${PORT} expands.
CMD .venv/bin/ainfera-mcp
