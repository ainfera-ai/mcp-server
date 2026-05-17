FROM python:3.12-slim

WORKDIR /app

# Install runtime deps directly (avoids `pip install .` PEP 517 build that
# needs README.md in the isolated build env, which Nixpacks doesn't copy).
RUN pip install --no-cache-dir \
    "mcp>=1.2.0" \
    "httpx>=0.27.0" \
    "pydantic>=2.6.0" \
    "uvicorn[standard]>=0.30"

# Copy source — read at import time, no install step needed.
COPY ainfera_mcp ./ainfera_mcp

EXPOSE 8000

CMD uvicorn ainfera_mcp.asgi:app --host 0.0.0.0 --port ${PORT:-8000}
