"""ASGI entry point for Railway / generic uvicorn deploys.

Wraps the FastMCP streamable-HTTP Starlette app and grafts on a /health
route so Railway's healthcheck (and any uptime monitor) gets a 200
without speaking MCP.
"""

from __future__ import annotations

from starlette.responses import JSONResponse
from starlette.routing import Route

from ainfera_mcp.server import mcp


async def _health(_request):
    return JSONResponse({"status": "ok"})


app = mcp.streamable_http_app()
app.router.routes.append(Route("/health", _health, methods=["GET"]))
