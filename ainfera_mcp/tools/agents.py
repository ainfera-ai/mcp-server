"""Agent tools: register_agent, get_agent, list_agents."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .._client import request


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def register_agent(name: str, description: str) -> dict[str, Any]:
        """Register a new Agent in Ainfera.

        Returns the Agent ID and a freshly minted JWS-signed AgentCard.
        """
        return await request(
            "POST",
            "/v1/agents",
            json={"name": name, "description": description},
        )

    @mcp.tool()
    async def get_agent(agent_id: str) -> dict[str, Any]:
        """Fetch an Agent by ID."""
        return await request("GET", f"/v1/agents/{agent_id}")

    @mcp.tool()
    async def list_agents(limit: int = 50) -> list[dict[str, Any]]:
        """List Agents owned by the authenticated Tenant."""
        result = await request("GET", "/v1/agents", params={"limit": limit})
        return result.get("items", []) if isinstance(result, dict) else result
