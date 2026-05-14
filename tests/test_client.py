import httpx
import pytest
import respx

from ainfera_mcp import _client


@respx.mock
async def test_request_sends_bearer_and_returns_json():
    route = respx.get("https://api.test.ainfera.ai/v1/agents/abc").mock(
        return_value=httpx.Response(200, json={"id": "abc", "name": "demo"})
    )

    result = await _client.request("GET", "/v1/agents/abc")

    assert result == {"id": "abc", "name": "demo"}
    assert route.called
    sent = route.calls.last.request
    assert sent.headers["authorization"] == "Bearer test-key"


@respx.mock
async def test_request_raises_on_error_status():
    respx.post("https://api.test.ainfera.ai/v1/inference").mock(
        return_value=httpx.Response(402, json={"error": "insufficient_funds"})
    )

    with pytest.raises(_client.AinferaAPIError) as exc:
        await _client.request("POST", "/v1/inference", json={"agent_id": "a"})

    assert exc.value.status == 402
    assert exc.value.body == {"error": "insufficient_funds"}


async def test_request_requires_api_key(monkeypatch):
    monkeypatch.delenv("AINFERA_API_KEY", raising=False)

    with pytest.raises(_client.AinferaAPIError) as exc:
        await _client.request("GET", "/v1/agents")

    assert exc.value.status == 401


@respx.mock
async def test_bearer_argument_overrides_env():
    route = respx.get("https://api.test.ainfera.ai/v1/agents").mock(
        return_value=httpx.Response(200, json={"items": []})
    )

    await _client.request("GET", "/v1/agents", bearer="override-key")

    assert route.calls.last.request.headers["authorization"] == "Bearer override-key"
