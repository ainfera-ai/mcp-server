"""ainfera://ontology resource — proxies to /ontology.json on the live API."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from .._client import request


def register(mcp: FastMCP) -> None:
    @mcp.resource("ainfera://ontology", mime_type="application/ld+json")
    async def ontology() -> str:
        """Ainfera Ontology v1.0 (JSON-LD)."""
        data = await request("GET", "/ontology.json")
        return json.dumps(data, indent=2)
