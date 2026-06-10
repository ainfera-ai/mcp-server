# Cloudflare Worker — optional edge in front of Railway MCP

**Production (2026-05-20):** `mcp.ainfera.ai` terminates on **Railway** (`x-railway-edge`), running `ainfera_mcp.asgi:app` from [ainfera-ai/mcp-server](https://github.com/ainfera-ai/mcp-server). See [`docs/RAILWAY_DEPLOY.md`](../docs/RAILWAY_DEPLOY.md).

This directory is an **optional** Cloudflare Worker reverse-proxy. Use it only if you want WAF/rate-limit/observability at the edge without changing the Railway origin.

## Deploy (optional)

```bash
cd cloudflare
wrangler login    # once, cached in ~/.config/.wrangler
# Set WORKER_ORIGIN to your Railway public URL before deploy
wrangler deploy
```

Verify against production (direct Railway or via worker):

```bash
curl -sS https://mcp.ainfera.ai/health
./smoke-mcp.sh
./smoke-mcp-keyed.sh
```

## Why a worker at all

DNS may stay Cloudflare-proxied (`cf-ray`) while the origin is Railway. A worker adds rate-limiting, API-key validation at the edge, or path rewrites without rotating the Railway service URL.

**Do not** point docs or smokes at Modal — Modal is an optional dev fallback only (`modal/deploy.py`).
