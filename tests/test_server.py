"""Smoke test: the FastMCP server registers every expected tool, resource, and prompt."""

import pytest

from ainfera_mcp.server import mcp


EXPECTED_TOOLS = {
    "register_agent",
    "get_agent",
    "mint_agent_card",
    "verify_agent_card",
    "inference",
    "topup_wallet",
    "get_wallet",
    "read_audit_chain",
    "verify_audit_chain",
    # AIN-243: `get_trust_score` retired with ATS/AAMC (2026-05-22).
    # Model trust now lives in Routing's `q_empirical` per Ontology v1.2.
}


async def test_all_ontology_tools_registered():
    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    missing = EXPECTED_TOOLS - names
    assert not missing, f"Missing MCP tools: {missing}"


async def test_quickstart_prompt_registered():
    prompts = await mcp.list_prompts()
    names = {p.name for p in prompts}
    assert "quickstart" in names


@pytest.mark.parametrize(
    "template_substring",
    ["ainfera://ontology", "ainfera://glossary/", "ainfera://concepts/"],
)
async def test_resource_templates_registered(template_substring):
    templates = await mcp.list_resource_templates()
    statics = await mcp.list_resources()
    uris = [t.uriTemplate for t in templates] + [str(r.uri) for r in statics]
    assert any(template_substring in u for u in uris), (
        f"No resource matching {template_substring}; got {uris}"
    )
