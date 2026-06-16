"""Verify MCP tools call the live API path surface (SDK 1.1.0 / AIN-79)."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from ainfera_mcp.server import mcp

_AGENT_ID = "00000000-0000-4000-8000-000000000001"
_TENANT_ID = "00000000-0000-4000-8000-000000000002"


@pytest.mark.parametrize(
    ("tool", "arguments", "method", "path", "json_body"),
    [
        (
            "register_agent",
            {"name": "demo", "tenant_id": _TENANT_ID},
            "POST",
            "/v1/agents/register",
            {"tenant_id": _TENANT_ID, "name": "demo"},
        ),
        (
            "get_agent",
            {"agent_id": _AGENT_ID},
            "GET",
            f"/v1/agents/{_AGENT_ID}",
            None,
        ),
        (
            "topup_wallet",
            {"agent_id": _AGENT_ID, "amount_usd": 1.0},
            "POST",
            "/v1/wallets/topup",
            {"agent_id": _AGENT_ID, "amount_usd": 1.0},
        ),
        (
            "get_wallet",
            {"agent_id": _AGENT_ID},
            "GET",
            f"/v1/wallets/{_AGENT_ID}",
            None,
        ),
        (
            "read_audit_chain",
            {"agent_id": _AGENT_ID, "limit": 5},
            "GET",
            f"/v1/audit/{_AGENT_ID}",
            None,
        ),
        (
            "verify_audit_chain",
            {"agent_id": _AGENT_ID},
            "GET",
            f"/v1/audit/{_AGENT_ID}/verify",
            None,
        ),
        (
            "verify_agent_card",
            {"card_jws": "a.b.c"},
            "POST",
            "/v1/agents/cards/verify",
            {"jws": "a.b.c"},
        ),
    ],
)
@respx.mock
async def test_tool_uses_live_api_path(tool, arguments, method, path, json_body):
    base = "https://api.test.ainfera.ai"
    route = respx.route(method=method, url=f"{base}{path}").mock(
        return_value=httpx.Response(
            200,
            json={"ok": True, "events": []} if tool == "read_audit_chain" else {"ok": True},
        )
    )

    await mcp.call_tool(tool, arguments)

    assert route.called
    sent = route.calls.last.request
    assert sent.method == method
    assert sent.url.path == path
    if json_body is not None:
        assert json.loads(sent.content) == json_body
