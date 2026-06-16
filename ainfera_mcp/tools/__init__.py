"""MCP tool registration. Each submodule exposes a `register(mcp)` function."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..guarded_tools import install_l1_precall_guard
from . import agent_card, agents, audit, inference, wallet


def register(mcp: FastMCP) -> None:
    agents.register(mcp)
    agent_card.register(mcp)
    inference.register(mcp)
    wallet.register(mcp)
    audit.register(mcp)
    install_l1_precall_guard(mcp)
