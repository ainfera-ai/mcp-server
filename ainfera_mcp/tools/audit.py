"""AuditChain tools: read_audit_chain, verify_audit_chain."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .._client import request


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def read_audit_chain(agent_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """Read the most recent AuditEvents for an Agent."""
        result = await request(
            "GET",
            f"/v1/audit/{agent_id}",
            params={"limit": limit},
        )
        return result.get("events", []) if isinstance(result, dict) else result

    @mcp.tool()
    async def verify_audit_chain(agent_id: str) -> dict[str, Any]:
        """Verify the hash chain integrity for an Agent's AuditChain.

        Returns `{ ok: bool, head: str, length: int, broken_at?: str }`.
        """
        return await request("GET", f"/v1/audit/{agent_id}/verify")
