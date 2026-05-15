"""Quickstart prompt — how to get started with Ainfera via MCP."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP


QUICKSTART = """\
You are helping the user get started with Ainfera, the Inference of AI Agents.

Walk them through these steps using the Ainfera MCP tools:

1. **Register an Agent**
   Use `register_agent` with a clear name and description.
   Returns an `agent_id` and a JWS-signed `AgentCard`.

2. **Top up the Wallet**
   Use `topup_wallet` with the `agent_id` and an `amount_usd` (start small, e.g. $5).

3. **Make an Inference call**
   Use `inference` with the `agent_id`, a `model` slug, and OpenAI-style `messages`.
   The response includes a Receipt URL pointing at the signed AuditEvent.

4. **Read and verify the AuditChain**
   Use `read_audit_chain` to see the most recent AuditEvents,
   then `verify_audit_chain` to confirm the hash chain is intact.

5. **Check TrustScore (optional)**
   Use `get_trust_score` to see the Agent's ATS v1.0 score (0-1000).

Read the `ainfera://ontology` resource for the canonical entity model
if you need deeper context on any primitive.
"""


def register(mcp: FastMCP) -> None:
    @mcp.prompt()
    def quickstart() -> str:
        """How do I get started with Ainfera?"""
        return QUICKSTART
