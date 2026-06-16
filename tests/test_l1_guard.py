"""L1 hard-deny pre-call guard tests."""

from __future__ import annotations

import httpx
import pytest
import respx
from mcp.server.fastmcp.exceptions import ToolError

from ainfera_mcp.l1_guard import (
    TOPUP_MAX_USD,
    TOPUP_MIN_USD,
    L1GuardResult,
    check_l1_guard,
    l1_match_label,
    set_scope_check_hook,
)
from ainfera_mcp.server import mcp

_AGENT_ID = "00000000-0000-4000-8000-000000000001"


@pytest.fixture(autouse=True)
def _clear_scope_hook():
    set_scope_check_hook(None)
    yield
    set_scope_check_hook(None)


@pytest.mark.parametrize(
    ("text", "label"),
    [
        ("Update the cap table for new equity split", "equity"),
        ("sign contract with vendor", "sign"),
        ("board resolution draft", "board"),
        ("offer letter for new hire", "hire"),
        ("bank transfer to supplier IBAN", "banking"),
        ("wire funds via payment rails", "payments"),
        ("execute a trading swap tokens order", "trading"),
        ("founder identity public statement", "identity"),
        ("medical records request", "medical"),
        ("family emergency contact", "family"),
    ],
)
def test_l1_match_label(text, label):
    assert l1_match_label(text) == label


def test_l1_match_label_none_for_benign():
    assert l1_match_label("list open issues and summarize") is None


@pytest.mark.parametrize(
    ("tool", "arguments"),
    [
        ("inference", {"agent_id": _AGENT_ID, "model": "auto", "messages": [{"role": "user", "content": "draft board resolution"}]}),
        ("register_agent", {"name": "demo", "tenant_id": _AGENT_ID, "description": "equity grant tracker"}),
        ("topup_wallet", {"agent_id": _AGENT_ID, "amount_usd": 5.0, "memo": "bank wire settlement"}),
    ],
)
def test_check_l1_guard_denies_sensitive_writes(tool, arguments):
    result = check_l1_guard(tool, arguments)
    assert not result.allowed
    assert result.reason and "L1 hard-deny" in result.reason


@pytest.mark.parametrize(
    ("amount", "reason_fragment"),
    [
        (None, "amount_usd is required"),
        ("not-a-number", "must be a number"),
        (0, "must be between"),
        (-1, "must be between"),
        (TOPUP_MAX_USD + 1, "must be between"),
        (TOPUP_MIN_USD - 0.001, "must be between"),
    ],
)
def test_topup_wallet_amount_bounds(amount, reason_fragment):
    args = {"agent_id": _AGENT_ID}
    if amount is not None:
        args["amount_usd"] = amount
    result = check_l1_guard("topup_wallet", args)
    assert not result.allowed
    assert result.reason and reason_fragment in result.reason


def test_topup_wallet_in_bounds_allowed():
    result = check_l1_guard(
        "topup_wallet",
        {"agent_id": _AGENT_ID, "amount_usd": TOPUP_MIN_USD},
    )
    assert result == L1GuardResult.allow()


@respx.mock
async def test_get_wallet_read_not_blocked():
    base = "https://api.test.ainfera.ai"
    route = respx.get(f"{base}/v1/wallets/{_AGENT_ID}").mock(
        return_value=httpx.Response(200, json={"balance_usd": 12.5})
    )

    await mcp.call_tool("get_wallet", {"agent_id": _AGENT_ID})

    assert route.called


@respx.mock
async def test_topup_wallet_missing_amount_raises_tool_error():
    with pytest.raises(ToolError, match="amount_usd"):
        await mcp.call_tool("topup_wallet", {"agent_id": _AGENT_ID})


@respx.mock
async def test_inference_l1_content_raises_tool_error():
    with pytest.raises(ToolError, match="L1 hard-deny"):
        await mcp.call_tool(
            "inference",
            {
                "agent_id": _AGENT_ID,
                "model": "auto",
                "messages": [{"role": "user", "content": "prepare offer letter for hire"}],
            },
        )


def test_scope_check_hook_can_deny():
    set_scope_check_hook(lambda _tool, _args: "scope denied: test")
    result = check_l1_guard("get_wallet", {"agent_id": _AGENT_ID})
    assert not result.allowed
    assert result.reason == "scope denied: test"


@respx.mock
async def test_scope_check_hook_blocks_tool_call():
    set_scope_check_hook(lambda _tool, _args: "out of scope")
    with pytest.raises(ToolError, match="out of scope"):
        await mcp.call_tool("get_wallet", {"agent_id": _AGENT_ID})
