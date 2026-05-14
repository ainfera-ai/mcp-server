"""Modal deployment for mcp.ainfera.ai.

Deploy:
    modal deploy modal/deploy.py

The Modal app mounts the ainfera_mcp package and serves the MCP protocol
over streamable HTTP. Custom domain `mcp.ainfera.ai` is routed via Cloudflare
Workers in front of the Modal web endpoint.
"""

from __future__ import annotations

import modal

app = modal.App("ainfera-mcp")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "mcp>=1.2.0",
        "httpx>=0.27.0",
        "pydantic>=2.6.0",
    )
    .add_local_python_source("ainfera_mcp")
)


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("ainfera-api")],
    min_containers=1,
    timeout=300,
)
@modal.asgi_app()
def mcp_app():
    """Expose the FastMCP server as an ASGI app for streamable HTTP transport."""
    from ainfera_mcp.server import mcp

    return mcp.streamable_http_app()
