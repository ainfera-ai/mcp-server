# Railway deploy — mcp.ainfera.ai

Production MCP runs on **Railway**, not Modal. DNS `mcp.ainfera.ai` → Railway edge (`x-railway-edge`).

## One-time founder action

1. Open Railway project → **ainfera-mcp** (or equivalent) service.
2. **Settings → Source** → set deploy branch to `main` on `ainfera-ai/mcp-server`.
3. **Settings → Deploy** → builder: Dockerfile (see repo root `Dockerfile` + `railway.json`).
4. **Redeploy** latest `main` (commit with `ainfera_mcp/asgi.py` + bearer middleware).

## Verify

```bash
curl -sS https://mcp.ainfera.ai/health
# {"status":"ok","service":"ainfera-mcp"}

cd mcp-server && ./cloudflare/smoke-mcp-keyed.sh
```

## Entrypoint

```
uvicorn ainfera_mcp.asgi:app --host 0.0.0.0 --port $PORT
```

`asgi.py` exports `http_app()` which includes `InboundBearerMiddleware` for per-request `Authorization: Bearer ainfera_*`.
