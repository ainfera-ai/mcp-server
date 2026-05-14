"""Inference tool: routes through Ainfera L2 and returns a Receipt URL."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .._client import request


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def inference(
        agent_id: str,
        model: str,
        messages: list[dict[str, Any]],
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """Make an Inference through Ainfera's L2 Routing.

        Returns the model response plus a Receipt URL pointing at the
        signed AuditEvent for this call.
        """
        return await request(
            "POST",
            "/v1/inference",
            json={
                "agent_id": agent_id,
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
            },
        )
