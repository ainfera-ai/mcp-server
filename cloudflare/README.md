# Cloudflare Worker — mcp.ainfera.ai → Modal reverse proxy

The Modal deployment at `hizrianraz--ainfera-mcp-mcp-app.modal.run` is
the source of truth for the MCP server. This worker fronts it on
`mcp.ainfera.ai` so external MCP clients use the branded URL.

## Deploy

```bash
cd cloudflare
wrangler login    # once, cached in ~/.config/.wrangler
wrangler deploy   # uploads worker.js + binds the mcp.ainfera.ai/* route
```

Verify:

```bash
curl -i -X POST https://mcp.ainfera.ai/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize",
       "params":{"protocolVersion":"2024-11-05",
                 "capabilities":{},
                 "clientInfo":{"name":"smoke","version":"0.0.1"}}}'
```

Expect a 200 with a streaming `event: message` payload containing the
server's `serverInfo` block (name=`ainfera`, version per the Modal
deploy).

## Why a worker not a CNAME

Modal's built-in custom-domain feature works for HTTPS termination,
but the Cloudflare layer is already there (DNS proxied, WAF + DDoS
shield, cache). Fronting Modal with a worker keeps that layer + lets
us add rate-limiting / API-key validation / observability later
without rotating endpoints.
