"""FastMCP entry point for the Ainfera MCP server."""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from . import prompts, resources, tools

# Hosts allowed past DNS-rebinding protection. The hosted deployment sits behind
# Cloudflare at mcp.ainfera.ai; the raw Modal URL is also reachable directly.
# DNS-rebinding wildcards only cover ":port" patterns, so the Modal host must be
# listed exactly — append it (and any others) via AINFERA_MCP_ALLOWED_HOSTS.
_DEFAULT_ALLOWED_HOSTS = ["mcp.ainfera.ai", "localhost", "127.0.0.1"]
_DEFAULT_ALLOWED_ORIGINS = ["https://mcp.ainfera.ai"]


def _csv_env(name: str) -> list[str]:
    return [v.strip() for v in os.environ.get(name, "").split(",") if v.strip()]


_transport_security = TransportSecuritySettings(
    allowed_hosts=_DEFAULT_ALLOWED_HOSTS + _csv_env("AINFERA_MCP_ALLOWED_HOSTS"),
    allowed_origins=_DEFAULT_ALLOWED_ORIGINS + _csv_env("AINFERA_MCP_ALLOWED_ORIGINS"),
)

mcp = FastMCP(
    name="ainfera",
    instructions=(
        "Ainfera MCP server — the Inference of AI Agents. "
        "Use the tools to register Agents, mint AgentCards, make Inference calls, "
        "manage Wallets, and read/verify AuditChains. "
        "Read the ainfera://ontology resource for the canonical entity model."
    ),
    transport_security=_transport_security,
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
