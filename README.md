# `ainfera-mcp` — Ainfera MCP Server

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

**The Inference of AI Agents, exposed as MCP tools.**

`ainfera-mcp` is the public [Model Context Protocol](https://modelcontextprotocol.io/) server for [Ainfera](https://ainfera.ai). Point any MCP-compatible client at `mcp.ainfera.ai`, paste your Ainfera API key, and Ainfera's L1–L5 primitives appear as tools:

- Register **Agents**
- Mint **AgentCards** (JWS-signed)
- Make **Inference** calls through L2 Routing
- Top up & inspect **Wallets**
- Read & verify **AuditChains** (hash-chained, signed AuditEvents)
- Read **TrustScore** (ATS v1.0, 0–1000)

No glue code, no SDK install — just MCP.

---

## Quickstart

### 1. Configure your MCP client

Hosted server (recommended):

```json
{
  "mcpServers": {
    "ainfera": {
      "url": "https://mcp.ainfera.ai",
      "headers": {
        "Authorization": "Bearer YOUR_AINFERA_API_KEY"
      }
    }
  }
}
```

Local stdio (development):

```bash
pip install ainfera-mcp
AINFERA_API_KEY=sk-... ainfera-mcp
```

```json
{
  "mcpServers": {
    "ainfera": {
      "command": "ainfera-mcp",
      "env": { "AINFERA_API_KEY": "sk-..." }
    }
  }
}
```

### 2. Ask your agent

> Register an Ainfera agent named "research-bot" and run an inference call against `gpt-5` asking it to summarize the latest arXiv submission on retrieval.

Your agent will call `register_agent`, `topup_wallet`, `inference`, and return a Receipt URL pointing at the signed AuditEvent.

---

## Tools

| Tool | Purpose |
|---|---|
| `register_agent` | Register a new Agent, returns ID + AgentCard |
| `get_agent` | Fetch an Agent by ID |
| `list_agents` | List Agents for the authenticated Tenant |
| `mint_agent_card` | Mint a fresh JWS-signed AgentCard |
| `verify_agent_card` | Verify a JWS AgentCard |
| `inference` | Make an Inference through L2 Routing |
| `topup_wallet` | Top up an Agent's Wallet |
| `get_wallet` | Balance + recent ledger entries |
| `read_audit_chain` | Most recent AuditEvents |
| `verify_audit_chain` | Verify hash chain integrity |
| `get_trust_score` | ATS v1.0 score (0–1000) |

Tool names match the canonical entity names in [Ontology v1.0 §2](https://ainfera.ai/ontology).

## Resources

| URI | Description |
|---|---|
| `ainfera://ontology` | Ainfera Ontology v1.0 (JSON-LD) |
| `ainfera://glossary/{term}` | Canonical definition of a glossary term |
| `ainfera://concepts/{entity}` | Concept page (markdown) for an Ontology entity |

## Prompts

| Name | Purpose |
|---|---|
| `quickstart` | Step-by-step guide for first-time Ainfera users |

---

## Configuration

| Env var | Default | Notes |
|---|---|---|
| `AINFERA_API_KEY` | — | Tenant API key (required for local stdio mode) |
| `AINFERA_API_BASE` | `https://api.ainfera.ai` | Override for staging / self-hosted |
| `AINFERA_MCP_TRANSPORT` | `stdio` | `stdio`, `sse`, or `http` |

For the hosted server, the API key is read from the `Authorization` header on each MCP request, so a single Modal deployment serves all tenants.

---

## Development

```bash
pip install -e ".[dev]"
pytest
```

The repo layout:

```
ainfera_mcp/
├── server.py          # FastMCP entry
├── _client.py         # Thin httpx client for the Ainfera API
├── tools/             # MCP tools (one module per primitive group)
├── resources/         # ainfera:// resources
└── prompts/           # MCP prompts
modal/
└── deploy.py          # Modal serverless deployment
tests/
```

## Deployment

Hosted at `mcp.ainfera.ai` via Modal:

```bash
modal deploy modal/deploy.py
```

Cloudflare Workers fronts the Modal web endpoint to serve the custom domain.

---

## License

Apache 2.0 — see [LICENSE](LICENSE).

## Links

- Ainfera: <https://ainfera.ai>
- Docs: <https://docs.ainfera.ai>
- MCP spec: <https://modelcontextprotocol.io/specification/>
