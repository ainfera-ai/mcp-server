"""Bearer extraction from inbound MCP HTTP requests."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import httpx
import pytest
import respx

from ainfera_mcp import _client


def _fake_request_ctx(headers: dict[str, str] | None):
    req = SimpleNamespace(headers=headers or {})
    ctx = SimpleNamespace(request=req)
    token = MagicMock()
    token.get.return_value = ctx
    return patch("mcp.server.lowlevel.server.request_ctx", token)


@respx.mock
async def test_bearer_from_mcp_authorization_header(monkeypatch):
    monkeypatch.delenv("AINFERA_API_KEY", raising=False)
    route = respx.get("https://api.test.ainfera.ai/v1/agents/abc").mock(
        return_value=httpx.Response(200, json={"id": "abc"})
    )

    with _fake_request_ctx({"authorization": "Bearer tenant-key-123"}):
        await _client.request("GET", "/v1/agents/abc")

    assert route.calls.last.request.headers["authorization"] == "Bearer tenant-key-123"


@respx.mock
async def test_explicit_bearer_beats_request_header(monkeypatch):
    monkeypatch.delenv("AINFERA_API_KEY", raising=False)
    route = respx.get("https://api.test.ainfera.ai/v1/agents").mock(
        return_value=httpx.Response(200, json={"items": []})
    )

    with _fake_request_ctx({"authorization": "Bearer from-header"}):
        await _client.request("GET", "/v1/agents", bearer="explicit-key")

    assert route.calls.last.request.headers["authorization"] == "Bearer explicit-key"
