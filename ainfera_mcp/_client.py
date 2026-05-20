"""Thin HTTP client for the Ainfera API.

Bearer auth resolves in this order:
1. `bearer` argument (per-request override)
2. `Authorization: Bearer` on the inbound MCP HTTP request (streamable-http)
3. `AINFERA_API_KEY` env var (server-wide default on Modal)
"""

from __future__ import annotations

import os
from typing import Any

import httpx

DEFAULT_BASE_URL = "https://api.ainfera.ai"
DEFAULT_TIMEOUT = 30.0


class AinferaAPIError(RuntimeError):
    def __init__(self, status: int, body: Any):
        super().__init__(f"Ainfera API {status}: {body}")
        self.status = status
        self.body = body


def _base_url() -> str:
    return os.environ.get("AINFERA_API_BASE", DEFAULT_BASE_URL).rstrip("/")


def _bearer_from_mcp_http_request() -> str | None:
    """Read tenant API key captured by InboundBearerMiddleware or request_ctx fallback."""
    from ainfera_mcp.middleware import get_inbound_bearer

    token = get_inbound_bearer()
    if token:
        return token

    try:
        from mcp.server.lowlevel.server import request_ctx
    except ImportError:
        return None

    try:
        ctx = request_ctx.get()
    except LookupError:
        return None

    req = getattr(ctx, "request", None)
    if req is None:
        return None

    headers = getattr(req, "headers", None)
    if headers is None:
        return None

    auth = headers.get("authorization") or headers.get("Authorization")
    if not auth:
        return None

    scheme, _, value = auth.partition(" ")
    if scheme.lower() != "bearer" or not value.strip():
        return None
    return value.strip()


def _resolve_bearer(bearer: str | None) -> str:
    token = bearer or _bearer_from_mcp_http_request() or os.environ.get("AINFERA_API_KEY")
    if not token:
        raise AinferaAPIError(
            401,
            "Missing Ainfera API key. Pass Authorization: Bearer on the MCP request "
            "or set AINFERA_API_KEY on the server.",
        )
    return token


async def request(
    method: str,
    path: str,
    *,
    bearer: str | None = None,
    json: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> Any:
    headers = {
        "Authorization": f"Bearer {_resolve_bearer(bearer)}",
        "Accept": "application/json",
        "User-Agent": "ainfera-mcp/0.1.0",
    }
    url = f"{_base_url()}{path}"

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.request(method, url, headers=headers, json=json, params=params)

    if resp.status_code >= 400:
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        raise AinferaAPIError(resp.status_code, body)

    if resp.status_code == 204 or not resp.content:
        return None
    return resp.json()
