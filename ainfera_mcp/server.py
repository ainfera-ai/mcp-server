"""FastMCP entry point for the Ainfera MCP server."""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from . import prompts, resources, tools

mcp = FastMCP(
    name="ainfera",
    instructions=(
        "Ainfera MCP server — prime inference for AI agents. "
        "Use the tools to register Agents, mint AgentCards, make Inference calls, "
        "manage Wallets, and read/verify AuditChains. "
        "Read the ainfera://ontology resource for the canonical entity model."
    ),
)

tools.register(mcp)
resources.register(mcp)
prompts.register(mcp)


def run() -> None:
    """Console-script entry. Transport selected by AINFERA_MCP_TRANSPORT env var."""
    transport = os.environ.get("AINFERA_MCP_TRANSPORT", "stdio")
    if transport == "stdio":
        mcp.run()
    elif transport == "sse":
        mcp.run(transport="sse")
    elif transport == "http":
        mcp.run(transport="streamable-http")
    else:
        raise SystemExit(f"Unknown AINFERA_MCP_TRANSPORT: {transport}")


if __name__ == "__main__":
    run()
