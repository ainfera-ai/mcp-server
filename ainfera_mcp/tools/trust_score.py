"""TrustScore tool: get_trust_score (ATS v1.0)."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .._client import request


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def get_trust_score(agent_id: str) -> dict[str, Any]:
        """Get an Agent's TrustScore (0-1000) from ATS v1.0."""
        return await request("GET", f"/v1/agents/{agent_id}/trust-score")
