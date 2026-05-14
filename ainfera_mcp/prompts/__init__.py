"""MCP prompt registration."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import quickstart


def register(mcp: FastMCP) -> None:
    quickstart.register(mcp)
