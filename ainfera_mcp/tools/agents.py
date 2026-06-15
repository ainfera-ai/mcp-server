"""Agent tools: register_agent, get_agent.

NOTE: list_agents has been removed — the live API has no generic
GET /v1/agents list endpoint.  To list all agents for a GitHub user
call GET /v1/users/{github_handle}/agents directly.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .._client import request


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def register_agent(tenant_id: str, name: str) -> dict[str, Any]:
        """Register a new Agent in Ainfera (provisions an Ed25519 keypair).

        Args:
            tenant_id: UUID of the owning Tenant.
            name: Human-readable agent name (1–255 chars).

        Returns the created Agent record.
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
