"""ainfera://concepts/{entity} resource — returns the concept page markdown."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .._client import request


def register(mcp: FastMCP) -> None:
    @mcp.resource("ainfera://concepts/{entity}", mime_type="text/markdown")
    async def concept(entity: str) -> str:
        """Concept page (markdown) for an Ontology entity."""
        data = await request("GET", f"/concepts/{entity}.md")
        if isinstance(data, str):
            return data
        return data.get("body", "") if isinstance(data, dict) else str(data)
