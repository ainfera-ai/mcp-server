"""MCP resource registration."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import concepts, glossary, ontology


def register(mcp: FastMCP) -> None:
    ontology.register(mcp)
    glossary.register(mcp)
    concepts.register(mcp)
