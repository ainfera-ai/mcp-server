"""MCP tool registration. Each submodule exposes a `register(mcp)` function."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import agent_card, agents, audit, inference, trust_score, wallet


def register(mcp: FastMCP) -> None:
    agents.register(mcp)
    agent_card.register(mcp)
    inference.register(mcp)
    wallet.register(mcp)
    audit.register(mcp)
    trust_score.register(mcp)
