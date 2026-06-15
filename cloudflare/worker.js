// Cloudflare Worker — mcp.ainfera.ai → Railway reverse proxy.
//
// Production runs on Railway (not Modal). See docs/RAILWAY_DEPLOY.md.
// DNS mcp.ainfera.ai → Railway edge (confirmed via x-railway-edge header).
//
// FOUNDER ACTION REQUIRED: set RAILWAY_ORIGIN below to the Railway
// internal URL for the ainfera-mcp service (e.g.
// https://ainfera-mcp-production.up.railway.app).  Find it in the
// Railway dashboard under the ainfera-mcp service → Settings → Domains.
//
// Pass-through semantics:
//   - All HTTP methods (POST for MCP handshake, GET for SSE streams)
//   - Authorization: Bearer ainfera_* headers
//   - request/response bodies untouched
//   - Streamable HTTP for SSE responses (no body buffering — required
//     for MCP's notifications/sampling capability)
//
// Deploy:
//   cd cloudflare/
//   wrangler deploy
//
// Custom domain `mcp.ainfera.ai` is set up via the Routes block in
// wrangler.toml + a CNAME (already in place on the ainfera.ai zone).

// STALE — was Modal; production moved to Railway. Replace with the
// Railway service URL from the dashboard before re-deploying this worker.
const MODAL_ORIGIN = "REPLACE_WITH_RAILWAY_URL";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const upstreamUrl = MODAL_ORIGIN + url.pathname + url.search;

    // Mirror the incoming request into one against the Modal origin.
    // `redirect: "manual"` so Modal-side 3xx propagate to the client
    // instead of being silently followed (MCP doesn't use redirects,
    // and following them in the worker would mask bugs).
    const upstreamReq = new Request(upstreamUrl, {
      method: request.method,
      headers: request.headers,
      body: request.body,
      redirect: "manual",
      // duplex: "half" is required by the Fetch spec when forwarding a
      // request body. CF runtime honours it on POST/PUT/PATCH.
      duplex: "half",
    });

    let upstreamRes;
    try {
      upstreamRes = await fetch(upstreamReq);
    } catch (err) {
      return new Response(
        JSON.stringify({
          jsonrpc: "2.0",
          error: {
            code: -32000,
            message: `upstream unreachable: ${err && err.message ? err.message : String(err)}`,
          },
          id: null,
        }),
        {
          status: 502,
          headers: { "Content-Type": "application/json" },
        },
      );
    }

    // Stream the response body straight back. Critical for the MCP
    // SSE stream — buffering the body would break streamable HTTP.
    // We pass headers verbatim; the worker doesn't rewrite Set-Cookie
    // because the API doesn't issue any.
    return new Response(upstreamRes.body, {
      status: upstreamRes.status,
      statusText: upstreamRes.statusText,
      headers: upstreamRes.headers,
    });
  },
};
