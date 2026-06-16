"""Agent tools: register_agent, get_agent."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .._client import request


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def register_agent(name: str, tenant_id: str) -> dict[str, Any]:
        """Register a new Agent in Ainfera.

        ``tenant_id`` must match the Tenant bound to the caller's API key.
        Returns the Agent record including its Ed25519 public key.
        """
        return await request(
            "POST",
            "/v1/agents/register",
            json={"tenant_id": tenant_id, "name": name},
        )

    @mcp.tool()
    async def get_agent(agent_id: str) -> dict[str, Any]:
        """Fetch an Agent by ID."""
        return await request("GET", f"/v1/agents/{agent_id}")
