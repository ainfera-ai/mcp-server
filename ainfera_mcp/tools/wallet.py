"""Wallet tools: topup_wallet, get_wallet."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .._client import request


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def topup_wallet(agent_id: str, amount_usd: float) -> dict[str, Any]:
        """Top up an Agent's Wallet by amount_usd."""
        return await request(
            "POST",
            f"/v1/agents/{agent_id}/wallet/topup",
            json={"amount_usd": amount_usd},
        )

    @mcp.tool()
    async def get_wallet(agent_id: str) -> dict[str, Any]:
        """Get an Agent's Wallet balance and recent ledger entries."""
        return await request("GET", f"/v1/agents/{agent_id}/wallet")
