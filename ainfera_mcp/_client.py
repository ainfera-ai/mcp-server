"""Thin HTTP client for the Ainfera API.

Bearer auth resolves in this order:
1. `bearer` argument (per-request override from MCP context)
2. `AINFERA_API_KEY` env var (server-wide default)
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


def _resolve_bearer(bearer: str | None) -> str:
    token = bearer or os.environ.get("AINFERA_API_KEY")
    if not token:
        raise AinferaAPIError(
            401,
            "Missing Ainfera API key. Set AINFERA_API_KEY env var or pass bearer.",
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
