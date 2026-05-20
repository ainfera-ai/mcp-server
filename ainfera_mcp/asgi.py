"""ASGI entry for Railway / uvicorn — http_app() + /health for probes."""

from __future__ import annotations

from starlette.responses import JSONResponse
from starlette.routing import Route

from ainfera_mcp.server import http_app

app = http_app()


async def _health(_request):  # type: ignore[no-untyped-def]
    return JSONResponse({"status": "ok", "service": "ainfera-mcp"})


app.router.routes.append(Route("/health", _health, methods=["GET"]))
