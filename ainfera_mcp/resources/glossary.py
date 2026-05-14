"""ainfera://glossary/{term} resource."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from .._client import request


def register(mcp: FastMCP) -> None:
    @mcp.resource("ainfera://glossary/{term}")
    async def glossary_term(term: str) -> str:
        """Canonical definition of a glossary term."""
        data = await request("GET", f"/glossary/{term}.json")
        return json.dumps(data, indent=2)
