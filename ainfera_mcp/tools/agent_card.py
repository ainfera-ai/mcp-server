"""AgentCard tools: mint_agent_card, verify_agent_card."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .._client import request


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def mint_agent_card(agent_id: str) -> dict[str, Any]:
        """Mint a fresh JWS-signed AgentCard for an existing Agent."""
        return await request("POST", f"/v1/agents/{agent_id}/card")

    @mcp.tool()
    async def verify_agent_card(card_jws: str) -> dict[str, Any]:
        """Verify a JWS-signed AgentCard.

        Returns the decoded card payload and verification status.
        """
        return await request("POST", "/v1/agents/cards/verify", json={"jws": card_jws})
