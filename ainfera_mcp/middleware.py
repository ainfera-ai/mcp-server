"""ASGI middleware — capture inbound Authorization for the request lifetime."""

from __future__ import annotations

import contextvars

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

inbound_bearer_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "ainfera_inbound_bearer",
    default=None,
)


def get_inbound_bearer() -> str | None:
    return inbound_bearer_var.get()


class InboundBearerMiddleware(BaseHTTPMiddleware):
    """Store `Authorization: Bearer` on a contextvar for all MCP tool calls."""

    async def dispatch(self, request: Request, call_next) -> Response:
        token: str | None = None
        auth = request.headers.get("authorization") or request.headers.get("Authorization") or ""
        if auth.lower().startswith("bearer "):
            token = auth[7:].strip() or None
        reset = inbound_bearer_var.set(token)
        try:
            return await call_next(request)
        finally:
            inbound_bearer_var.reset(reset)
